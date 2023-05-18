# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_login import UserMixin

from apps import db, login_manager
import datetime
import random as rdm
from apps.authentication.util import hash_pass

class Users(db.Model, UserMixin):

    __tablename__ = 'Users'

    id = db.Column(db.Integer, primary_key=True)
    nomeCompleto = db.Column(db.String)
    cpf = db.Column(db.String(11), unique=True)
    email = db.Column(db.String(64), unique=True)
    matricula = db.Column(db.String(12), unique=True)
    periodo = db.Column(db.Integer)
    cadastro = db.Column(db.String(16))
    password = db.Column(db.LargeBinary)

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


@login_manager.user_loader
def user_loader(id):
    return Users.query.filter_by(id=id).first()


@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    user = Users.query.filter_by(email=email).first()
    return user if user else None
