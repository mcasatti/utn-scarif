# Creación de las entidades necesarias para el sistema de análisis
# cienciométrico (y de congresos) SCARIF
#########################################################
#					ENTIDADES
#########################################################

######################################################
# PERSONA
######################################################
# Clase abstracta "Persona" de la cual heredar
create class Persona if not exists extends V abstract;
create property Persona.nombre string (notnull true);

######################################################
# ARTICULO
######################################################
# Clase Artículo, que va a ser central en la parte de cienciometría
create class Articulo if not exists extends V;
create property Articulo.titulo string (notnull true);
create property Articulo.keywords EMBEDDEDLIST STRING;
create property Articulo.text string;
create property Articulo.oid string;
create property Articulo.orcid string;


######################################################
# AUTOR
######################################################
create class Autor if not exists extends Persona;
# los datos identificatorios deberían ser comunes a la persona
create property Autor.email string;
# create property Autor.tipo string;		# Tipificar. Investigador, Docente, Estudiante, etc. Unico?
create property Autor.oid string; # Definir despues qué puede ser, email, oid, etc.
create property Autor.pais string;

######################################################
# KEYWORD
######################################################
# Las etiquetas es mejor colocarlas como nodo o como tags en cada entidad?
# MODELADO COMO UNA LISTA DE STRINGS EN CADA ARTICULO
# create class Keyword if not exists extends V;
# create property Keyword.keyword string (notnull true);

######################################################
# PUBLICACION
######################################################
create class Publicacion if not exists extends V;
create property Publicacion.titulo string (notnull true);
create property Publicacion.periodicidad string;
create property Publicacion.ISBN string; # Ver otros clasificadores
create property Publicacion.fecha date;
create property Publicacion.tipos EMBEDDEDSET string; # Una lista de tipos? Un nodo TipoPublicación!!! Revista,Libro,Tesis,PaginasWeb,Actas,Etc.
create property Publicacion.pais string;

######################################################
# INSTITUCION
######################################################
create class Institucion if not exists extends V;
create property Institucion.nombre string;
create property Institucion.tipo string;

######################################################
# EVENTO
######################################################
create class Evento if not exists extends V;
create property Evento.nombre string;
create property Evento.tipo string;    # Congreso, Jornadas, Workshop, etc.
create property Evento.fecha date; 
create property Evento.pais string; 	# Lugar físico donde se desarrolla?

######################################################
# CATEGORIA
######################################################
# Categorizacion de Scopus para las áreas de la ciencia 
# (https://github.com/plreyes/Scopus/blob/master/ASJC%20Codes%20with%20levels.csv)
create class Categoria if not exists extends V;
create property Categoria.categoria string (notnull true);
create property Categoria.codigoScopus string;

#########################################################
#					RELACIONES
#########################################################

######################################################
# PUBLICADO EN (Articulo -> Publicacion)
######################################################

# Las entidades PUBLICACION y REFERENCIA son mejor modeladas como relaciones entre Articulos, Publicaciones, etc
create class publicadoEn if not exists extends E; # Articulo -> Publicacion
create property publicadoEn.fechaPublicacion date (notnull true);
create property publicadoEn.oid string;
# el modelo original plantea la fecha en el articulo
# creo que es un mejor enfoque que la fecha esté en la relación
# de esa manera un articulo publicado en distintos lados
# puede tener distintas fechas

create class Referencia if not exists extends V;
create property Referencia.accessed datetime;		#Fecha en la cual se consultó



create class referenciaA if not exists extends E; # Articulo -> Referencia -> Publicación
# Una referencia puede referenciar un articulo, publicado en una publicacion dada, en una pagina indicada, etc.
# Esto quizá sea conveniente modelarlo como un nodo que apunta a una publicación y un articulo, AL MISMO TIEMPO


# Una categoria puede tener una relacion a si misma
create class categoriaPadre if not exists extends E; # Categoria -> Categoria
# Un articulo pertenece a una categoría determinada (la mas detallada posible)
create class categoriaScopus if not exists extends E; # Articulo -> Categoria, Publicacion -> Categoria 	

# Un autor es autorDe en uno o más artículos. Ver si se establece el orden de autoría (para medir importancia de aporte)
create class autorDe if not exists extends E;
create property autorDe.orden integer;

# Un autor colaboraCon otros autores, obtenido de los grupos de autores de un artículo
create class colaboraCon if not exists extends E;

# Un articulo puede ser expuesto en algún Evento
create class expuestoEn if not exists extends E;

# ALGUNAS REFERENCIAS
/*
https://www.scimagojr.com/shapeofscience/
https://images.webofknowledge.com/images/help/WOS/hp_subject_category_terms_tasca.html
https://mjl.clarivate.com/help-center
https://www.leydesdorff.net/map06/texts/map06.pdf
https://github.com/plreyes/Scopus/blob/master/ASJC%20Codes%20with%20levels.csv
https://pg.edu.pl/documents/611754/75313317/asjc
https://arxiv.org/pdf/1511.00735.pdf
*/

# Un autor tiene una o más filiaciones que lo asocia a una o mas instituciones
create class filiacionA if not exists extends E;