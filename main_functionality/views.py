from django.shortcuts import get_object_or_404, redirect, render
from blend_algorithms.blend_generator import TeaBlender
from .forms import TeaBlendForm
from .models import *
from django.core.paginator import Paginator

def index_page(request):
    return render(request, 'content.html')

def tea_blend_creater_form(request):
    if request.method == 'POST':
        form = TeaBlendForm(request.POST)
        if form.is_valid():

            theme = form.cleaned_data['theme']

            user_request = UserRequest.objects.create(
                theme=theme.name if theme else "",
                taste_type=form.cleaned_data['taste_type'],
                tea_type=form.cleaned_data['tea_type'],
                no_additives=form.cleaned_data['no_additives'],
                price_range=form.cleaned_data['price_range']
            )

            blend_data = TeaBlender.create_blend_from_request(user_request)
                
            if not blend_data or not blend_data['teas']:
                return render(request, 'tea_blend_creater.html', {
                    'form': form,
                    'error': 'Не удалось составить купаж по вашим параметрам.'
                })
            
            request.session['user_request_id'] = user_request.id
            request.session['blend_data'] = {
                'name': blend_data['name'],
                'tea_ids': [tea.id for tea in blend_data['teas']],
                'additive_ids': [add.id for add in blend_data['additives']],
                'subtaste_id': blend_data['subtaste'].id if blend_data.get('subtaste') else None,
            }
            
            blend = Blend.objects.create(
                name=blend_data['name'],
                theme=blend_data.get('theme'),
                subtaste=blend_data.get('subtaste'),
            )
            
            blend.teas.set(blend_data['teas'])
            
            if blend_data['additives']:
                blend.additives.set(blend_data['additives'])

            request.session['current_blend_id'] = blend.id
            
            return render(request, 'tea_blend_result.html', {
                'blend': blend,
                'user_request': user_request,
                'is_saved': False,
            })
    else:
        form = TeaBlendForm()
    
    return render(request, 'tea_blend_creater.html', {
        'form': form,
        'price_value': 1000
    })

def save_blend(request):
    blend_id = request.session.get('current_blend_id')
    
    if not blend_id:
        return redirect('tea_blend_creater_form')
    
    try:
        blend = Blend.objects.get(id=blend_id)
        blend.is_saved = True
        blend.save()
        
        return render(request, 'tea_blend_result.html', {
                'blend': blend,
                'is_saved': True,
            })
        
    except Blend.DoesNotExist:
        return redirect('tea_blend_creater_form')
    
def regenerate_blend(request):
    user_request_id = request.session.get('user_request_id')
    
    if not user_request_id:
        return redirect('tea_blend_creater_form')
    
    try:
        user_request = UserRequest.objects.get(id=user_request_id)
    except UserRequest.DoesNotExist:
        return redirect('tea_blend_creater_form')
    
    old_blend_id = request.session.get('current_blend_id')
    
    blend_data = TeaBlender.create_blend_from_request(user_request)
    
    if not blend_data or not blend_data['teas']:
        return redirect('tea_blend_creater_form')
    
    new_blend = Blend.objects.create(
        name=blend_data['name'],
        theme=blend_data.get('theme'),
        subtaste=blend_data.get('subtaste')
    )
    
    new_blend.teas.set(blend_data['teas'])
    
    if blend_data['additives']:
        new_blend.additives.set(blend_data['additives'])
    
    request.session['current_blend_id'] = new_blend.id
    
    if old_blend_id:
        try:
            old_blend = Blend.objects.get(id=old_blend_id)
            if not old_blend.is_saved:
                old_blend.delete()
        except Blend.DoesNotExist:
            pass
    
    return render(request, 'tea_blend_result.html', {
        'blend': new_blend,
        'user_request': user_request,
        'is_saved': False,
    })

def catalog_view(request):
    blends = Blend.objects.filter(is_saved=True).order_by('-created_at')

    paginator = Paginator(blends, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'catalog.html', {
        'page_obj': page_obj,
        'blends': page_obj.object_list,
    })

def blend_detail(request, blend_id):
    blend = get_object_or_404(Blend, id=blend_id, is_saved=True)
    
    return render(request, 'tea_blend_result.html', {
        'blend': blend,
        'is_saved': True,
    })

def about_view(request):
    return render(request, 'about.html')