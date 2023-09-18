
from typing import Any
from django import forms
from .models import Service,Template
from repository.models import Repository

class TemplateForm(forms.ModelForm):
    
    def save(self, commit: bool = ...) -> Any:
        template = super().save(commit)
        id = self.data['repository'] if 'repository' in self.data else None
        if id:
            repository = Repository.objects.get(id=id)
            repository.templates.add(template)
            repository.save()
            
        return template
      
    class Meta:
       model = Template
       fields = ['name','service'] 