# coding=utf-8

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Usuario, Categoria, Produto, Base

engine = create_engine('postgresql://catalog:catalog@localhost/catalog')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Cria Usuario Inicial
Usuario01 = Usuario(nome="Davi Prada Hoffmann",
                    email="davi@teste.com.br",
                    imagem="https://pbs.twimg.com/profile_images/"
                    "870297475453788160/NC1s4asd_400x400.jpg")
session.add(Usuario01)
session.commit()

print "Usuário inserido!"

# Cria Categorias
CategoriaBasquete = Categoria(usuario_id=1, nome="Futebol")
session.add(CategoriaBasquete)
session.commit()

CategoriaFutebol = Categoria(usuario_id=1, nome="Futebol Americano")
session.add(CategoriaFutebol)
session.commit()

CategoriaVolei = Categoria(usuario_id=1, nome="Basquete")
session.add(CategoriaVolei)
session.commit()

print "Categorias inseridos!"

# Produtos Categoria Futebol
produtoFutebolCamiseta = Produto(nome="Camisa Barcelona I 19 Nike"
                                 " - Masculina",
                                 descricao="Tecido De Poliester De"
                                 " Elevado Desempenho",
                                 tipo="camisetas",
                                 preco="159,90",
                                 quantidade="1",
                                 categoria_id=1,
                                 usuario_id=1)
session.add(produtoBasqueteAgasalho)
session.commit()
produtoFutebolCamiseta2 = Produto(nome="Camisa do Vasco da Gama - Masculina",
                                  descricao="Camisa do Vasco da Gama II"
                                  " 2019 Diadora - Masculina",
                                  tipo="camisetas",
                                  preco="150,87",
                                  quantidade="1",
                                  categoria_id=1,
                                  usuario_id=1)
session.add(produtoBasqueteBandeira)
session.commit()
produtoBasqueteBermuda = Produto(nome="Bermuda Juventus",
                                 descricao="Bermuda Juventus Shadow - "
                                 "Masculina",
                                 tipo="bermudas",
                                 preco="69,90",
                                 quantidade="1",
                                 categoria_id=1,
                                 usuario_id=1)
session.add(produtoBasqueteCamiseta)
session.commit()

# Produtos Categoria Futebol Americano
produtoFutebolAgasalho = Produto(nome="Bola de Futebol Americano",
                                 descricao="Bola de Futebol Americano "
                                 "Vollo Oficial 9",
                                 tipo="bolas",
                                 preco="159,90",
                                 quantidade="5",
                                 categoria_id=2,
                                 usuario_id=1)
session.add(produtoFutebolAgasalho)
session.commit()
produtoFutebolAmericanoCamiseta = Produto(nome="Camiseta New Era"
                                          " New England Patriots",
                                          descricao="Camiseta New"
                                          " Era New England Patriots"
                                          " - Masculina",
                                          tipo="camisetas",
                                          preco="198,99",
                                          quantidade="7",
                                          categoria_id=2,
                                          usuario_id=1)
session.add(produtoFutebolBandeira)
session.commit()
produtoFutebolAmericanoCasemita2 = Produto(nome="Camiseta New Era"
                                           " Washington Redskins Vein Year",
                                           descricao="Camiseta New "
                                           "Era Washington Redskins "
                                           "Vein Year - Masculina",
                                           tipo="camisetas",
                                           preco="210,50",
                                           quantidade="3",
                                           categoria_id=2,
                                           usuario_id=1)
session.add(produtoFutebolCamiseta)
session.commit()

# Produtos Categoria Basquete
produtoBasqueteTenis = Produto(nome="Tenis Nike Fly By Low",
                               descricao="Tenis Nike Fly "
                               "By Low Masculino",
                               tipo="tenis",
                               preco="199,99",
                               quantidade="5",
                               categoria_id=3,
                               usuario_id=1)
session.add(produtoVoleiAgasalho)
session.commit()
produtoVoleiBandeira = Produto(nome="Bola de Basquete",
                               descricao="Bola de Basquete"
                               " Spalding Fastbreak NBA 7",
                               tipo="bolas",
                               preco="89,99",
                               quantidade="7",
                               categoria_id=3,
                               usuario_id=1)
session.add(produtoVoleiBandeira)
session.commit()
produtoVoleiCamiseta = Produto(nome="Tenis Nike Air Precision II",
                               descricao="Tenis Nike Air Precision"
                               " II Masculino",
                               tipo="tenis",
                               preco="249,99",
                               quantidade="3",
                               categoria_id=3,
                               usuario_id=1)
session.add(produtoVoleiCamiseta)
session.commit()

print "Produtos inseridos!"
