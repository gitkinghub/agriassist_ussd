from django.utils import timezone
from django.shortcuts import render
from .models import UssdSession, UssdSessionState, UssdUser
from .utils import USSDMenuHandler
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

'''
Process USSD request from AfricasTalking
    
Expected POST data:
- sessionId: Unique session identifier
- serviceCode: USSD code dialed (e.g., *384*123#)
- phoneNumber: User's phone number (+254XXXXXXXXX)
- text: User's navigation path (e.g., "1*2*3")
'''

@csrf_exempt
def ussd_callback(request):
    if request.method != "POST":
        return HttpResponse("END Invalid request", content_type="text/plain")
    
    # Extract data from AfricasTalking callback
    session_id = request.POST.get('sessionId')
    service_code = request.POST.get('serviceCode')
    phone_number = request.POST.get('phoneNumber')
    text = request.POST.get('text')
    
    # validate required fields
    if not all([session_id, service_code, phone_number]):
        return HttpResponse("END Invalid request", content_type="text/plain")
    
    # get or create session and state and get user
    user, _ = UssdUser.objects.get_or_create(phone_number=phone_number)
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
    
    # Return plain text response
    return HttpResponse(response_prefix + response_text, content_type="text/plain")
