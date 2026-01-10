from django.db.models import Q
from main_functionality.models import BaseTea, Taste, Subtaste, SubtasteAdditive, TasteSubtaste, Additive, Theme

class TeaBlender:
    
    @staticmethod
    def create_blend_from_request(user_request):
        theme = Theme.objects.filter(name=user_request.theme).first() if user_request.theme else None

        subtastes = Subtaste.objects.filter(name=user_request.taste_type)
        subtaste = subtastes.first() if subtastes.exists() else None

        teas = BaseTea.objects.filter(tea_type=user_request.tea_type)

        selected_teas = []
        if subtaste:
            related_tastes = Taste.objects.filter(
                tastesubtaste__subtaste=subtaste
            )
            teas_with_taste = teas.filter(
                tastes__in=related_tastes
            ).distinct()
            
            if teas_with_taste.exists():
                selected_teas = list(teas_with_taste.order_by('?')[:2])

        if len(selected_teas) < 2:
            excluded_ids = [t.id for t in selected_teas]
            remaining_teas = teas.exclude(id__in=excluded_ids) if excluded_ids else teas
            
            additional_needed = 2 - len(selected_teas)
            if remaining_teas.exists():
                selected_teas.extend(list(remaining_teas.order_by('?')[:additional_needed]))

        selected_additives = []
        
        if not user_request.no_additives:
            if theme and theme.additives.exists():
                theme_additives = theme.additives.all()
                selected_additives = list(theme_additives[:3])
            elif subtaste:
                additive_relations = SubtasteAdditive.objects.filter(
                    subtaste=subtaste
                ).select_related('additive')[:3]
                selected_additives = [rel.additive for rel in additive_relations]
        
        if theme:
            theme_part = theme.name
        else:
            theme_part = "Персональный"
        
        blend_name = f"{theme_part}: {user_request.tea_type} - {user_request.taste_type}"
        
        if theme and theme.subtastes.exists() and not subtaste:
            recommended_subtaste = theme.subtastes.first()
            if recommended_subtaste:
                subtaste = recommended_subtaste
        
        return {
            'name': blend_name,
            'teas': selected_teas,
            'additives': selected_additives,
            'subtaste': subtaste,
            'theme': theme,
        }