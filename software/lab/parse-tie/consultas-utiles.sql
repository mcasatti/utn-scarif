/* Consultas Autores, los Artículos que han escrito y la cantidad de autores  que tiene el artículo en total */
match {class: Autor, as: a}-autorDe-{class: Articulo, as: r} return r.titulo, count(a) as Autores group by r.titulo

/* Para un articulo dado obtener sus autores */
match {class: Articulo, as: art, where: (@rid=#36:22)}<-autorDe-{class: Autor, as: aut} return $elements

/* Para una institución dado obtener sus autores */
match {class: Autor, as: aut}-filiacionA-{class: Institucion, as: inst, where: (@rid=#48:31)} return $elements

