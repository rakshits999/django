from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import UserSerializer, LoginSerializer, HistorySerializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import History
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework import permissions
from rest_framework.decorators import api_view, authentication_classes, permission_classes
import openai

openai.api_key = "your api key"



class hello(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        print(user)
        return Response({"message": "Hello, authenticated user!"})
# ================================================================================================


class RegistrationAPIView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            account = serializer.save()  
            response_data = {
                'status': 'True',
                'message': "Registration Successful!",
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        
# ==========================================================================================================



class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data.get('user')
            if user:
                token, created = Token.objects.get_or_create(user=user)
                return Response({
                    'status': "True",
                    'name': user.first_name,
                    'email': user.email,
                    'token': token.key  
                }, status=status.HTTP_200_OK)
            else:
                return Response({'status': "False", 'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# ============================= View code for logout =============================


class LogoutAPIView(APIView):
    def post(self, request):
        if request.method == 'POST':
            request.user.auth_token.delete()
            return Response({'message':"Logout sucessful"},status=status.HTTP_200_OK)
        else:
            return Response({'status': "False", 'error': 'Token not found'}, status=status.HTTP_400_BAD_REQUEST)
        
# =================================chatgpt code =================================================


@api_view(['POST', 'GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def journal(request, pk=1):
    user = request.user
    user_question = request.data.get('question')

    user_history = History.objects.filter(user=user).order_by('-id')[:2]      
    last_two_entries = []
    for entry in user_history:
        last_two_entries.append({"role": "user", "content": entry.question})
        last_two_entries.append({"role": "assistant", "content": entry.answer})

    user_questions = {"role": "user", "content": user_question}
    last_two_entries.append(user_questions)
    print(last_two_entries)


    result = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=last_two_entries,
        stream=True
    )

    response_text = ""
    for chunk in result:
        response_text += chunk.choices[0].delta.get("content", "")
        print(chunk.choices[0].delta.get("content", ""), end="", flush=True)

    # Save the user question and response to the database
    history_entry = History(user=user, question=user_question, answer=response_text)
    history_entry.save() 

    return Response({"response": response_text})

class DeleteUserHistoryView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def delete(self, request, pk=1):
        try:
            user = request.user.id
            print(user)
            
            # user_id = user.id
            history_records = History.objects.filter(user=user)
            history_records.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except History.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
