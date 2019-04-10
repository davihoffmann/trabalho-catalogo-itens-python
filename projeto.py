#!/usr/bin/env python
# -*- coding: utf-8 -*-
from io import BytesIO
from flask import Flask, render_template, request, redirect, \
    jsonify, url_for, flash, send_file
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from database_setup import Base, Usuario, Categoria, Produto
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalogo"

engine = create_engine('sqlite:///catalogo-itens.db',
                       connect_args={'check_same_thread': False},
                       poolclass=StaticPool, echo=True)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Rota da tela de Login
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

# Configuração login - Google
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Realiza o login através da api do Google,
    # validando o token de acesso
    # Obten o código de autorização e atualiza o
    # código de autorização
    # Verifica se o token de acesso é válido e armazena
    # na variável login_session
    # Busca as informações do usuário e realiza o login
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data

    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps
                                 ('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    user_id = getUsuarioID(data["email"])
    if not user_id:
        user_id = createUsuario(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h5>Bem Vindo, '
    output += login_session['username']
    output += '!</h5>'
    flash("Voce esta logado como %s" % login_session['username'])
    print "done!"
    return output

# Configuração para logout da conta Google
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

# Sair do sistema
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
            del login_session['provider']
            login_session.clear()
        flash("Voce foi desconectado com sucesso.")
        return redirect(url_for('listaCategorias'))
    else:
        flash("Voce nao esta logado!")
        return redirect(url_for('listaCategorias'))


# Cria usuário
def createUsuario(login_session):
    novoUsuario = Usuario(nome=login_session['username'], email=login_session[
        'email'], imagem=login_session['picture'])
    session.add(novoUsuario)
    session.commit()
    user = session.query(Usuario).filter_by(email=login_session['email']).one()
    return user.id


# Busca Informação do Usuário
def getUsuarioInfo(user_id):
    user = session.query(Usuario).filter_by(id=user_id).one()
    return user


# Busca Usuário pelo e-mail
def getUsuarioID(email):
    try:
        user = session.query(Usuario).filter_by(email=email).one()
        return user.id
    except Exception:
        return None

# CATEGORIAS
# Lista todas as categorias
@app.route('/')
@app.route('/categoria/')
def listaCategorias():
    categorias = session.query(Categoria).order_by(asc(Categoria.nome))
    if 'username' not in login_session:
        return render_template('categoriasPublic.html', categorias=categorias)
    else:
        return render_template('categorias.html', categorias=categorias)

# Criar ama nova categoria
@app.route('/categoria/nova/', methods=['GET', 'POST'])
def novaCategoria():
    # Cria uma nova categoria se o usuário estiver autenticado no sistema.
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        novaCategoria = Categoria(
            nome=request.form['nome'], usuario_id=login_session['user_id'])
        session.add(novaCategoria)
        flash('Nova Categoria %s foi criada com sucesso!' % novaCategoria.nome)
        session.commit()
        return redirect(url_for('listaCategorias'))
    else:
        return render_template('novaCategoria.html')

# Alterar uma categoria cadastrada
@app.route('/categoria/<int:categoria_id>/editar/', methods=['GET', 'POST'])
def editarCategoria(categoria_id):
    categoriaEditada = session.query(
        Categoria).filter_by(id=categoria_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if categoriaEditada.usuario_id != login_session['user_id']:
        return "<script>function myFunction() " \
               "{alert('Você não está autorizado a editar " \
               "esta categoria.');}" \
               "</script><body onload='myFunction()'>"
    if request.method == 'POST':
        categoriaEditada.nome = request.form['nome']
        flash('Categoria %s editada com sucesso' % categoriaEditada.nome)
        session.commit()
        return redirect(url_for('listaCategorias'))
    else:
        return render_template('editarCategoria.html',
                               categoria=categoriaEditada)

# Excluir uma categoria cadastrada
@app.route('/categoria/<int:categoria_id>/excluir/', methods=['GET', 'POST'])
def excluirCategoria(categoria_id):
    # Verifica se esta autenticado e se o usuario pode excluir a categoria
    categoriaExcluir = session.query(Categoria) \
        .filter_by(id=categoria_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if categoriaExcluir.usuario_id != login_session['user_id']:
        return "<script>function myFunction() " \
               "{alert('Você não está autorizado a excluir" \
               " esta categoria.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(categoriaExcluir)
        flash('%s categoria excluida com sucesso!' % categoriaExcluir.nome)
        session.commit()
        return redirect(url_for('listaCategorias', categoria_id=categoria_id))
    else:
        return render_template('excluirCategoria.html',
                               categoria=categoriaExcluir)

# Busca todas as categorias e retorna do fomato de JSON
@app.route('/categoria/JSON')
def categoriaJSON():
    categorias = session.query(Categoria).all()
    return jsonify(categorias=[categoria.serialize
                               for categoria in categorias])

# Busca o detalhe da categoria e retorna do fomato de JSON
@app.route('/categoria/<int:id>/JSON')
def categoriaDetalhadaJSON(id):
    categoria = session.query(Categoria) \
        .filter_by(id=id).one()

    if not categoria:
        abort(400)

    return jsonify(Categoria=categoria.serialize)

# Lista todos os produtos de uma categoria
@app.route('/categoria/<int:categoria_id>/')
@app.route('/categoria/<int:categoria_id>/produtos/')
def listaProdutos(categoria_id):
    categoria = session.query(Categoria).filter_by(id=categoria_id).one()
    usuario = getUsuarioInfo(categoria.usuario_id)
    produtos = session.query(Produto) \
        .filter_by(categoria_id=categoria_id).all()

    print('username' not in login_session)
    print(usuario.id)
    print(login_session['user_id'])

    if 'username' not in login_session or \
            usuario.id != login_session['user_id']:
        return render_template('produtosPublicos.html',
                               produtos=produtos, categoria=categoria,
                               usuario=usuario)
    else:
        return render_template('produtos.html',
                               produtos=produtos, categoria=categoria,
                               usuario=usuario)

# PRODUTO
# Cria um novo produto
@app.route('/categoria/<int:categoria_id>/produtos/novo/',
           methods=['GET', 'POST'])
def novoProdutoCategoria(categoria_id):
    if 'username' not in login_session:
        return redirect('/login')
    categoria = session.query(Categoria).filter_by(id=categoria_id).one()
    if login_session['user_id'] != categoria.usuario_id:
        return "<script>function myFunction() {alert('Você não está " \
               "autorizado a adicionar produtos nesta categoria. " \
               "Por favor, crie sua própria categoria para adicionar" \
               " produtos.');}</script><body onload='myFunction(" \
               ")'> "
    if request.method == 'POST':
        novoProduto = Produto(nome=request.form['nome'],
                              descricao=request.form['descricao'],
                              tipo=request.form['tipo'],
                              preco=request.form['preco'],
                              quantidade=request.form['quantidade'],
                              categoria_id=categoria_id,
                              usuario_id=categoria.usuario_id)
        session.add(novoProduto)
        session.commit()
        flash('Produto %s foi adicionado com sucesso' % novoProduto.nome)
        return redirect(url_for('listaProdutos', categoria_id=categoria_id))
    else:
        return render_template('novoProduto.html', categoria_id=categoria_id)

# Edita um Produto cadastrado
@app.route('/categoria/<int:categoria_id>/produtos/<int:produto_id>/editar',
           methods=['GET', 'POST'])
def editarProduto(categoria_id, produto_id):
    if 'username' not in login_session:
        return redirect('/login')
    produtoEditado = session.query(Produto).filter_by(id=produto_id).one()
    categoria = session.query(Categoria).filter_by(id=categoria_id).one()
    if login_session['user_id'] != categoria.usuario_id:
        return "<script>function myFunction() {alert('Você não está " \
               "autorizado a editar produtos nesta categoria. " \
               "Por favor, crie sua própria categoria para editar " \
               "produtos.');}</script><body onload='myFunction()'> "
    if request.method == 'POST':
        if request.form['nome']:
            produtoEditado.nome = request.form['nome']
        if request.form['descricao']:
            produtoEditado.descricao = request.form['descricao']
        if request.form['tipo']:
            produtoEditado.tipo = request.form['tipo']
        if request.form['preco']:
            produtoEditado.preco = request.form['preco']
        if request.form['quantidade']:
            produtoEditado.quantidade = request.form['quantidade']
        session.add(produtoEditado)
        session.commit()
        flash('Produto editado com sucesso!')
        return redirect(url_for('listaProdutos', categoria_id=categoria_id))
    else:
        return render_template('editarProduto.html',
                               categoria_id=categoria_id,
                               produto_id=produto_id,
                               item=produtoEditado)

# Exclui um Produto cadastrado
@app.route('/categoria/<int:categoria_id>/produtos/<int:produto_id>/excluir',
           methods=['GET', 'POST'])
def excluirProduto(categoria_id, produto_id):
    if 'username' not in login_session:
        redirect('/login')
    categoria = session.query(Categoria).filter_by(id=categoria_id).one()
    produtoExcluido = session.query(Produto).filter_by(id=produto_id).one()
    if login_session['user_id'] != categoria.usuario_id:
        return "<script>function myFunction() {alert('Você não está " \
               "autorizado a excluir produtos nesta categoria. " \
               "Por favor, crie sua própria categoria para excluir " \
               "produtos.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(produtoExcluido)
        flash('Produto excluido com sucesso!')
        session.commit()
        return redirect(url_for('listaProdutos', categoria_id=categoria_id))
    else:
        return render_template('excluirProduto.html',
                               produto=produtoExcluido,
                               categoria_id=categoria_id)

# Busca todos os produtos de uma categoria e retorna no formato de JSON
@app.route('/categoria/<int:categoria_id>/produtos/JSON')
def listaProdutosJSON(categoria_id):
    categoria = session.query(Categoria).filter_by(id=categoria_id).one()
    produtos = session.query(Produto).filter_by(
        categoria_id=categoria_id).all()
    return jsonify(Produtos=[produto.serialize for produto in produtos])

# Busca o detalhe do produto de uma categoria e retorna no formato de JSON
@app.route('/categoria/<int:categoria_id>/produtos/<int:produto_id>/JSON')
def listaProdutoDetalheJSON(categoria_id, produto_id):
    produto = session.query(Produto).filter_by(
        id=produto_id).one()
    return jsonify(Produtos=produto.serialize)


if __name__ == '__main__':
    app.debug = True
    app.secret_key = 'full_stack_nanodegree_key'
    app.run(host='0.0.0.0', port=5000)
