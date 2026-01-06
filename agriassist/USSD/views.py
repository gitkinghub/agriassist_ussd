from django.utils import timezone
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import generics
from rest_framework import status
from .models import UssdSession, UssdSessionState, UssdUser
from .utils import USSDMenuHandler

class USSDCallbackView(APIView):
    '''
    Process USSD request from AfricasTalking
        
    Expected POST data:
    - sessionId: Unique session identifier
    - serviceCode: USSD code dialed (e.g., *384*123#)
    - phoneNumber: User's phone number (+254XXXXXXXXX)
    - text: User's navigation path (e.g., "1*2*3")
    '''
    
    def post(self, request):
        # Extract data from AfricasTalking callback
        session_id = request.data.get('sessionId')
        service_code = request.data.get('serviceCode')
        phone_number = request.data.get('phoneNumber')
        text = request.data.get('text')
        
        # validate required fields
        if not all([session_id, service_code, phone_number]):
            return Response(
                {'error': 'Missing required fields'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # get or create session and state and get user
        user = UssdUser.objects.get(phone_number=phone_number)
        session, _ = UssdSession.objects.get_or_create(
            session_id=session_id, 
            defaults={
                'user': user,
                'service_code': service_code,
                'is_active': True,
            }
        )
        
        session_state, _ = UssdSessionState.objects.get_or_create(
            session=session, 
            defaults={
                'current_menu': 'main_menu',
                'menu_history': [],
                'temp_data': {}
            }
        )
        
        handler= USSDMenuHandler(user, session, session_state, text)
        response_text, is_end = handler.process()
        
        # Update session if ended
        if is_end:
            session.is_active = False
            session.ended_at = timezone.now()
            session.save()
            print(f"[USSD] Session ended: {session_id}")
        
        # Format response for AfricasTalking
        # CON = Continue (show menu and wait for input)
        # END = End session (final message)
        response_prefix = "END " if is_end else "CON "
        formatted_response = response_prefix + response_text
        
        # Return plain text response
        return Response(
            formatted_response,
            content_type='text/plain',
            status=status.HTTP_200_OK
        )
