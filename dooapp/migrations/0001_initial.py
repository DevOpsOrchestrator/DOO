# Generated by Django 4.2.5 on 2023-09-30 17:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('repository', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=50, null=True, verbose_name='Grupo')),
            ],
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=50, null=True, verbose_name='Serviço')),
                ('status', models.IntegerField(choices=[(1, 'Ativo'), (2, 'Inativo')], default=1)),
                ('grupo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='services', to='dooapp.group')),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=50, null=True, verbose_name='Equipe')),
            ],
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.IntegerField(null=True)),
                ('titulo', models.CharField(max_length=100, verbose_name='Titulo')),
                ('descricao', models.TextField(max_length=255, null=True, verbose_name='Descrição')),
                ('prioridade', models.IntegerField(choices=[(1, 'Emergencial'), (2, 'Urgente'), (3, 'Alta'), (4, 'Media'), (5, 'Baixa')], default=4)),
                ('data_inicio', models.DateTimeField(auto_now_add=True)),
                ('data_fim', models.DateTimeField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Template',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('filename', models.CharField(null=True)),
                ('repository', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='templates', to='repository.repository')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dooapp.service')),
            ],
        ),
        migrations.CreateModel(
            name='Provision',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prompt', models.TextField(null=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='provision_template', to='dooapp.template')),
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='provision_ticket', to='dooapp.ticket')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='provisions', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='group',
            name='equipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='groups', to='dooapp.team'),
        ),
    ]
