# Generated by Django 2.2 on 2020-04-05 21:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.TextField()),
                ('playfield_cards', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_name', models.TextField()),
                ('used_playfield_cards', models.TextField()),
                ('current_game', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='demo.Game')),
            ],
        ),
    ]
