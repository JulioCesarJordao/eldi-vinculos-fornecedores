from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render,redirect,get_object_or_404
from .models import Pendencia,Loja,Importacao
from .forms import ImportForm,AcompanhamentoForm,AtualizacaoMassaForm
from .services import importar,acompanhar,pode_importar,acompanhar_em_massa

@login_required
def home(request):
    return render(request,'home.html',{'pode_importar':pode_importar(request.user)})

@permission_required('eldi.view_pendencia',raise_exception=True)
def pending(request):
    query = request.GET.get('q','')[:200]
    qs = Pendencia.objects.select_related('produto','loja','responsavel','ultima_importacao').order_by('produto__codigo')
    if query: qs=qs.filter(Q(produto__codigo__icontains=query)|Q(produto__descricao__icontains=query))
    loja=request.GET.get('loja','')
    state=request.GET.get('situacao','')
    if loja.isdigit(): qs=qs.filter(loja_id=int(loja))
    if state in Pendencia.Situacao.values: qs=qs.filter(situacao=state)
    page=Paginator(qs,50).get_page(request.GET.get('page'))
    latest={i.loja_id:i.pk for i in Importacao.objects.filter(situacao='concluida').order_by('referencia')}
    for p in page: p.nao_verificado=latest.get(p.loja_id)!=p.ultima_importacao_id
    return render(request,'pending.html',{'page':page,'q':query,'lojas':Loja.objects.all(),'estados':Pendencia.Situacao.choices})

@permission_required('eldi.change_pendencia',raise_exception=True)
def update(request,pk):
    p=get_object_or_404(Pendencia.objects.select_related('produto','loja'),pk=pk)
    form=AcompanhamentoForm(request.POST or None,initial={'responsavel':p.responsavel_id,'situacao':p.situacao,'observacao':p.observacao})
    if request.method=='POST' and form.is_valid():
        try:
            acompanhar(pk,request.user,**form.cleaned_data)
        except ValidationError as exc: form.add_error(None,exc)
        else:
            messages.success(request,'Atualização salva com histórico.')
            return redirect('pending')
    return render(request,'update.html',{'p':p,'form':form,'bloqueada':p.situacao=='confirmada'})

@permission_required('eldi.add_importacao',raise_exception=True)
def upload(request):
    form=ImportForm(request.POST or None,request.FILES or None)
    result=None
    if request.method=='POST' and form.is_valid():
        f=form.cleaned_data['arquivo']
        try:
            result=importar(f.read(),form.cleaned_data['loja'],form.cleaned_data['referencia'],request.user,f.name)
        except ValidationError as exc: form.add_error(None,exc)
        else: messages.success(request,'Importação concluída. Produto ausente não confirma regularização.')
    return render(request,'upload.html',{'form':form,'result':result})


@permission_required('eldi.change_pendencia', raise_exception=True)
def bulk_update(request):
    form = AtualizacaoMassaForm(request.POST or None)
    confirmar = False
    selected = []
    if request.method == 'POST' and form.is_valid():
        selected = list(form.cleaned_data['pendencias'])
        if request.POST.get('etapa') == 'confirmar':
            try:
                total = acompanhar_em_massa(
                    [p.pk for p in selected], request.user,
                    form.cleaned_data['situacao'], form.cleaned_data['responsavel'], form.cleaned_data['observacao'])
            except ValidationError as exc:
                form.add_error(None, exc)
            else:
                messages.success(request, f'{total} pendência(s) atualizada(s). Histórico individual preservado.')
                return redirect('pending')
        elif request.POST.get('etapa') != 'editar':
            confirmar = True
    return render(request, 'bulk.html', {'form':form,'confirmar':confirmar,'selected':selected})
