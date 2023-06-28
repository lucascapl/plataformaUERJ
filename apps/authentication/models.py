# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_login import UserMixin
from sqlalchemy import Column, Integer, String,ForeignKey,Float, func, desc,LargeBinary
from sqlalchemy.orm import relationship
from apps import db, login_manager
import datetime
import random as rdm
from apps.authentication.util import hash_pass

class Aluno(db.Model, UserMixin):

    __tablename__ = 'Aluno'

    id = Column(Integer, primary_key=True)
    nomeCompleto = Column(String)
    cpf = Column(String(11), unique=True)
    email = Column(String(64), unique=True)
    matricula = Column(String(12), unique=True)
    periodo = Column(Integer)
    cadastro = Column(String(16))
    password = Column(LargeBinary)
    turmaID = Column(Integer, ForeignKey('Turma.id'))

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            if property == 'password':
                value = hash_pass(value)  # we need bytes here (not plain str)

            setattr(self, property, value)

    def __repr__(self):
        return str(self.username)
    
    def dataCadastro(self):
        dataHoraAtual = datetime.datetime.now()
        dataFormatada = dataHoraAtual.strftime("%d/%m/%y")
        horaFormatada = dataHoraAtual.strftime("%H:%M")

        dataHoraFormatada = f"{dataFormatada} - {horaFormatada}"
        self.cadastro = dataHoraFormatada

    def geraMatricula(self):
        dataHoraAtual = datetime.datetime.now()
        matricula = dataHoraAtual.year
        matricula = str(matricula)
        for _ in range(0,8):
            numMatricula = rdm.randint(0,9)
            numToken = str(numMatricula)
            matricula = matricula + numToken
        self.matricula = matricula

class Professor(db.Model, UserMixin):

    __tablename__ = 'Professor'

    id = Column(Integer, primary_key=True)
    nomeCompleto = Column(String)
    cpf = Column(String(11), unique=True)
    email = Column(String(64), unique=True)
    matricula = Column(String(12), unique=True)
    dataCadastro = Column(String(16))
    password = Column(LargeBinary)
    turmaID = Column(Integer, ForeignKey('Turma.id'))

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            if property == 'password':
                value = hash_pass(value)  # we need bytes here (not plain str)

            setattr(self, property, value)

    def __repr__(self):
        return str(self.username)
    
    def dataCadastro(self):
        dataHoraAtual = datetime.datetime.now()
        dataFormatada = dataHoraAtual.strftime("%d/%m/%y")
        horaFormatada = dataHoraAtual.strftime("%H:%M")

        dataHoraFormatada = f"{dataFormatada} - {horaFormatada}"
        self.cadastro = dataHoraFormatada

    def geraMatricula(self):
        dataHoraAtual = datetime.datetime.now()
        matricula = dataHoraAtual.year
        matricula = str(matricula)
        for _ in range(0,8):
            numMatricula = rdm.randint(0,9)
            numToken = str(numMatricula)
            matricula = matricula + numToken
        self.matricula = 'p'+matricula

class Disciplina(db.Model):

    __tablename__ = 'Disciplina'

    id = Column(Integer, primary_key=True)
    nome = Column(String)

class Turma(db.Model):

    __tablename__ = 'Turma'

    id = Column(Integer, primary_key=True)
    professorID = Column(Integer, ForeignKey('Professor.id'))
    disciplinaID = Column(Integer, ForeignKey('Disciplina.id'))
    relacaoAlunos = relationship('Aluno')

@login_manager.user_loader
def user_loader(id):
    return Aluno.query.filter_by(id=id).first()


@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    user = Aluno.query.filter_by(email=email).first()
    return user if user else None
