from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Usuario
from .forms import UsuarioForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

class PerfilView(LoginRequiredMixin, UpdateView):
    model = Usuario
    form_class = UsuarioForm
    template_name = 'usuarios/perfil.html'
    success_url = reverse_lazy('perfil')
    
    def get_object(self, queryset=None):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Perfil atualizado com sucesso!')
        return super().form_valid(form)

@login_required
def perfil(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('perfil')
    else:
        form = UsuarioForm(instance=request.user)
    
    return render(request, 'usuarios/perfil.html', {'form': form}) 