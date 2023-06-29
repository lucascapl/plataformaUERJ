# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import render_template, redirect, request, url_for
from flask_login import (
    current_user,
    login_user,
    logout_user
)

from apps import db, login_manager
from apps.authentication import blueprint
from apps.authentication.forms import LoginForm, CreateAccountForm, CreateAccountProfessorForm
from apps.authentication.models import Aluno, Professor, Disciplina, Turma

from apps.authentication.util import verify_pass, hash_pass


@blueprint.route('/')
def route_default():
    return redirect(url_for('authentication_blueprint.login'))


# Login & Registration

@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    if 'login' in request.form:

        # read form data
        matricula = request.form['matricula']
        password = request.form['password']

        # Locate user by cpf
        user = Aluno.query.filter_by(matricula=matricula).first()

        # Check the password
        if user and verify_pass(password, user.password):

            login_user(user)
            return redirect(url_for('authentication_blueprint.route_default'))

        # Something (user or pass) is not ok
        return render_template('accounts/login.html',
                               msg='Wrong user or password',
                               form=login_form)

    if not current_user.is_authenticated:
        return render_template('accounts/login.html',
                               form=login_form)
    return redirect(url_for('home_blueprint.index'))


@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    create_account_form = CreateAccountForm(request.form)
    if 'register' in request.form:

        cpf = request.form['cpf']
        email = request.form['email']

        # Check usename exists
        user = Aluno.query.filter_by(cpf=cpf).first()
        if user:
            return render_template('accounts/register.html',
                                   msg='CPF já registrado',
                                   success=False,
                                   form=create_account_form)

        # Check email exists
        user = Aluno.query.filter_by(email=email).first()
        if user:

            return render_template('accounts/register.html',
                                   msg='Email já registrado',
                                   success=False,
                                   form=create_account_form)

        # else we can create the user
        user = Aluno(**request.form)
        user.geraMatricula()
        user.dataCadastro()
        db.session.add(user)
        db.session.commit()

        return render_template('accounts/register.html',
                               msg='User created please <a href="/login">login</a>',
                               success=True,
                               form=create_account_form)

    else:
        return render_template('accounts/register.html', form=create_account_form)
    
@blueprint.route('/cadastrarDisciplina', methods=['POST'])
def cadastrarDisciplina():
    if request.method == 'POST':
        nomesMaterias = request.json["nomes"]
        
        for nomeMateria in nomesMaterias:
            novaDisciplina = Disciplina()
            novaDisciplina.nome = nomeMateria
            db.session.add(novaDisciplina)
        
        db.session.commit()
        return '200'
    else:
        return '500'
    
@blueprint.route('/registrarProfessores', methods=['POST'])
def registrarProfessores():
    if request.method == 'POST':
        nomesProfessores = request.json["nomes"]
        senha = request.json["senha"]
        cpfs = request.json["cpfs"]

        for i in range(len(nomesProfessores)):
            nome = nomesProfessores[i]
            cpf = cpfs[i]

            novoProfessor = Professor()
            novoProfessor.nomeCompleto = nome
            emailProfessor = novoProfessor.nomeCompleto.replace(" ", "")
            emailProfessor = emailProfessor.lower()
            emailProfessor = emailProfessor + 'teste@example.com'
            novoProfessor.email = emailProfessor
            novoProfessor.password = hash_pass(senha)
            novoProfessor.geraMatricula()
            novoProfessor.dataCadastro()
            novoProfessor.cpf = cpf  # Adiciona o CPF ao professor
            db.session.add(novoProfessor)

        db.session.commit()
        return '200'
    else:
        return '500'

@blueprint.route('/registrarAlunos', methods=['POST'])
def registrarAlunos():
    if request.method == 'POST':
        nomesAlunos = request.json["nomes"]
        senha = request.json["senha"]
        cpfs = request.json["cpfs"]

        for i in range(len(nomesAlunos)):
            nome = nomesAlunos[i]
            cpf = cpfs[i]

            novoAluno = Aluno()
            novoAluno.nomeCompleto = nome
            emailProfessor = novoAluno.nomeCompleto.replace(" ", "")
            emailProfessor = emailProfessor.lower()
            emailProfessor = emailProfessor + 'teste@example.com'
            novoAluno.email = emailProfessor
            novoAluno.password = hash_pass(senha)
            novoAluno.geraMatricula()
            novoAluno.dataCadastro()
            novoAluno.cpf = cpf  # Adiciona o CPF ao professor
            db.session.add(novoAluno)

        db.session.commit()
        return '200'
    else:
        return '500'


@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('authentication_blueprint.login'))


# Errors

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('home/page-404.html'), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('home/page-500.html'), 500
