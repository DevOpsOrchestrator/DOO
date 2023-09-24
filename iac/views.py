from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.http import HttpResponse
from .models import InventoryParameter, PlaybookParameter, AnsibleModuleVariable

def getHtmlInventoryParameter(inventoryParameter,value=''):
    html = None

    if inventoryParameter:
        if inventoryParameter.type.type in ['input', 'text', 'file', 'password']:
                html = '''<span class="input-group-text" >{name}</span>
                        <input type="{type}" name="param__{name}" class="form-control" aria-describedby="{name}" value="{value}">
                    '''.format(name=inventoryParameter.name, type=inventoryParameter.type.type, value=value)
        elif inventoryParameter.type.type in ['radio', 'checkbox']:
                if inventoryParameter.value:
                    html = '<span class="input-group-text" >{name}</span> '.format(
                        name=inventoryParameter.name)
                    for v in inventoryParameter.value.split(','):
                        checked = 'checked' if v == value else None
                        html += '''<input type="{type}" name="param__{name}" value="{value}" {checked}>
                                   <label>{value}</label><br>'''.format(value=inventoryParameter.value, 
                                                                        type=inventoryParameter.type.type, 
                                                                        name=inventoryParameter.name,
                                                                        checked = checked)
        elif inventoryParameter.type.type in ['select']:
                html = '<span class="input-group-text" >{name}</span> '.format(
                    name=inventoryParameter.name)
                if inventoryParameter.value:
                    html += '<select class="form-select" name="param__{name}"> '.format(
                        name=inventoryParameter.name)
                    for v in inventoryParameter.value.split(','):
                        selected = 'selected' if v == value else None
                        html += '<option value="{value}" {selected}>{value}</option> '.format(
                            value=v.strip(), selected=selected)
                    html += '</select> '
    return html

def getHtmlAnsibleModuleVariable(AnsibleModuleVariables, modal):
     html = ''
     
     selectHidden = []

     for ansibleModuleVariable in AnsibleModuleVariables:
          fontRequired = ' fw-bold ' if ansibleModuleVariable.required else ''
          required = 'required' if ansibleModuleVariable.required else ''
          hidden = '' if ansibleModuleVariable.required else 'hidden'
          htmlSelect = ''

          if not ansibleModuleVariable.required:   
            selectHidden.append(f'<option value="{ansibleModuleVariable.name}">{ansibleModuleVariable.name}</option> ')

          html +=f'<div id="option{ansibleModuleVariable.name}" class="input-group mb-2" {hidden}> '
          html +=f'<span class="input-group-text {fontRequired}" >{ansibleModuleVariable.name}</span> '

          if ansibleModuleVariable.variable_type in ['path','raw','str'] or not ansibleModuleVariable.variable_type:
               html+=f'<input type="text" class="form-control" name="param__{ansibleModuleVariable.name}" {required}> '
          elif ansibleModuleVariable.variable_type == 'bool':
               html+= '<div class="input-group-text"> '
               html+=f'<input class="form-check-input mt-0" type="checkbox" name="param__{ansibleModuleVariable.name}" {required}> </div>'
          elif ansibleModuleVariable.variable_type == 'dict':
               html+=f'<input type="text" aria-label="key" class="form-control" name="param__{ansibleModuleVariable.name}" {required}> '
               html+=f'<input type="text" aria-label="val" class="form-control" name="param__{ansibleModuleVariable.name}" {required}> '
               html+=f'<button class="btn btn-outline-secondary" type="button" > <span class="bi-plus"> </span> </button> '
               html+=f'<div class="input-group" id="{ansibleModuleVariable.name}DictDiv"> </div> <br>'
          elif ansibleModuleVariable.variable_type in ['float','int']:
               html+=f'<input type="number" class="form-control" name="param__{ansibleModuleVariable.name}" {required}> '
          elif ansibleModuleVariable.variable_type == 'list':
               if ansibleModuleVariable.choices:
                    html += f'<select class="form-select" name="param__{ansibleModuleVariable.name}" {required}> '
                    for v in ansibleModuleVariable.choices.split('|'):
                        html += f'<option value="{v.strip()}">{v.strip()}</option> '
                    html += '</select> '
               else:
                    html+=f'<input type="text" class="form-control" name="param__{ansibleModuleVariable.name}" {required}> '
                    html+=f'<button class="btn btn-outline-secondary" type="button" > <span class="bi-plus"> </span> </button> '
                    html+=f'<div class="input-group" id="{ansibleModuleVariable.name}ListDiv"> </div> '
          
          html +='</div>'
          
          htmlSelect +=f'<div class="input-group mb-2" > '
          htmlSelect +=f'<select class="form-select" id="selectOptionHidden{modal}" > '
          for sh in selectHidden:
               htmlSelect += sh
          htmlSelect +=f'</select> <button class="btn btn-outline-secondary" type="button" onclick="showOption(\'{modal}\')" > <span class="bi-plus"> </span> </button>  </div> '

          
     return htmlSelect+html
 
def getHtmlAnsibleModuleVariableTemplate(AnsibleModuleVariables):
     html = ''
     
     selectHidden = []

     for ansibleModuleVariable in AnsibleModuleVariables:
          fontRequired = ' fw-bold ' if ansibleModuleVariable.required else ''
          required = 'required' if ansibleModuleVariable.required else ''
          hidden = '' if ansibleModuleVariable.required else 'hidden'
          htmlSelect = ''

          if not ansibleModuleVariable.required:   
            selectHidden.append(f'<option value="{ansibleModuleVariable.name}">{ansibleModuleVariable.name}</option> ')

          html +=f'<div id="option{ansibleModuleVariable.name}" class="input-group mb-2" {hidden}> '
          html +=f'<span class="input-group-text {fontRequired}" >{ansibleModuleVariable.name}</span> '

          html+=f'''
            <select class="form-select" id="inputTypeSelect" name="inputType__{ansibleModuleVariable.name}">
                <option selected>Choose Input Type</option>
                <option value="1">Text</option>
            </select>
            <span class="input-group-text" >Label</span>
            <input type="text" class="form-control" name="param__{ansibleModuleVariable.name}" {required}>
          '''
          
          html +='</div>'
          
          htmlSelect +=f'<div class="input-group mb-2" > '
          htmlSelect +=f'<select class="form-select" id="selectOptionHiddenTemplate" > '
          for sh in selectHidden:
               htmlSelect += sh
          htmlSelect +=f'</select> <button class="btn btn-outline-secondary" type="button" onclick="showOption(\'Template\')" > <span class="bi-plus"> </span> </button>  </div> '

          
     return htmlSelect+html
                    


###################################### metodos para url ######################################

def InventoryParameterHTML(request, parametro):

    try:

        inventoryParameter = InventoryParameter.objects.get(id=int(parametro)) 
        html = getHtmlInventoryParameter(inventoryParameter)

        return HttpResponse(html)
    
    except ObjectDoesNotExist:
        return None
    
def playbookParameterHTML(request, parametro):

    try:

        playbookParameter = PlaybookParameter.objects.get(id=int(parametro)) 
        html = getHtmlInventoryParameter(playbookParameter)

        return HttpResponse(html)
    
    except ObjectDoesNotExist:
        return None

def ansibleModuleVariableHTML(request, parametro):

    try:
        modal = request.GET['modal'] if 'modal' in request.GET else None
        ansibleModuleVariable = AnsibleModuleVariable.objects.filter(module=int(parametro)).order_by('name')
        html = getHtmlAnsibleModuleVariable(ansibleModuleVariable, modal)

        return HttpResponse(html)
    
    except ObjectDoesNotExist:
        return None
    
def ansibleModuleVariableTemplateHTML(request, parametro):

    try:
        ansibleModuleVariable = AnsibleModuleVariable.objects.filter(module=int(parametro)).order_by('name')
        html = getHtmlAnsibleModuleVariableTemplate(ansibleModuleVariable)

        return HttpResponse(html)
    
    except ObjectDoesNotExist:
        return None
    


