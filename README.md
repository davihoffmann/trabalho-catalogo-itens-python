# FULLSTACK NANODEGREE - Catalogo de Itens

## Descrição
* Você desenvolverá um aplicativo que fornece uma lista de itens em uma variedade de categorias, bem como um sistema de registro e autenticação de usuários. Usuários registrados terão a capacidade de postar, editar e excluir seus próprios itens.

## Requerimentos
* Python 2.7.x
* Vagrant
* VirtualBox

## Configurando o Projeto
* Fazer a instalação do Vagrant e o VirtualBox
* Fazer a clonagem do repositório fullstack-nanodegree-vm
* Fazer o download deste projeto e salvar o mesmo dentro da pasta "vagrant"

## Como iniciar
* Acesse o diretorio vagrant, dentro do repositório fullstack-nanodegree-vm e insira o seguinte comando:
<code>vagrant up</code>

* Para acessar a máquina virtual, utilize o seguinte comando:
<code>vagrant ssh</code>

* Após acessar a máquina virtual,  mude para o diretório /vagrant, utilizando o seguinte comando:
<code>cd /vagrant</code>


## Configuração do banco de dados
* Dentro do diretorio do projeto, existem 2 arquivos para executar para fazer a configuração do banco de dados

* Execute primeiramente o seguinte comando:
<code>python database_setup.py</code>

* Então execute o seguinte comando para realizar a inserção dos dados no banco:
<code>python database_insert.py</code>

## Executando a aplicação
* Entrar no diretório vagrant localizado da máquina virtual e acessar a pasta do projeto, e executar o arquivo projeto.py:
<code>python app.py</code>

* O servidor estará sendo executado na porta 5000