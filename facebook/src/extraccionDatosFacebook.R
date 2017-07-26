# TODO: Hay una discrepancia del 1% entre los likes que traen el post y la lista de Likes individuales de getPosts. Ejemplo: "148528951956339_917191005090126"
library(Rfacebook)

# Token temporal que caduca cada 1 hora. TODO: Automatizar token
fbToken <- "EAAE2YoZAnC9EBABforopEkNZCy7XYnnTlA7glzmZAq77YMUULMwgMtJt6fI2TGSWK9gXDu9ovcXagZCGAzggaQoQ500YC5OB0QghV0DD4Aa1EI1rdVZA1agxW5dBG4mzHozK6j6xcB3ZARED3etQQW9u1CTAzIAAA2XV68Pq8Kv8Fv5knOy1IMQhackKta0FcZD"

dataPath <- "/home/pablo/GDrive/BigSocialData/facebook/data/raw"

# idBaldassi <- "148528951956339"
ExtraerDatosFacebook <- function(candidato, fbToken){
  print(sprintf("Extrayendo datos candidato: %s", candidato))
  paginaCandidato <- getPage(candidato, token = fbToken, n=5000, since = '2015/06/01')
  
  # Empezando el loop de descarga de comentarios
  # obtengo el primero para armar estructura de datasets
  print(sprintf("Extrayendo comentarios candidato: %s", candidato))
  postId <- paginaCandidato$id[1]
  primerComentario <- getPost(post = postId, token = fbToken)
  posts <- primerComentario[["post"]]
  likes <- primerComentario[["likes"]]
  if(nrow(likes) > 0){
    likes$post_id <- postId 
  }
  comments <- primerComentario[["comments"]]
  
  # Recorro restantes anexando informacion
  for (i in 2:nrow(paginaCandidato)) {
    postId <- paginaCandidato$id[i]
    comentario <- getPost(post = postId, token = fbToken)

    posts <- rbind(posts, comentario[["post"]])

    tmpLikes <- comentario[["likes"]]
    if(!is.null(tmpLikes )){
      tmpLikes$post_id <- postId
    }
    likes <- rbind(likes, tmpLikes)

    comments <- rbind(comments, comentario[["comments"]])
    if(i %% 25 == 0){
      print(sprintf("Post %i de %i", i, nrow(paginaCandidato)))
      }
  }
  
  comments$post_number <- stringr::str_split_fixed(comments$id, "_",2)[,2]
  likes$post_number <- stringr::str_split_fixed(likes$post_id, "_",2)[,2]
  posts$post_number <- stringr::str_split_fixed(posts$id, "_",2)[,2]
  
  # Escribir a csv
  # TODO: Crear carpetas con el script
  print(sprintf("Escribiendo datos a disco del candidato %s", candidato))
  dir.create(dataPath)
  dir.create(paste0(dataPath,candidato))
  
  readr::write_csv(comments, paste0(dataPath,candidato,"/comments.csv"))
  readr::write_csv(likes, paste0(dataPath,candidato,"/likes.csv"))
  readr::write_csv(posts, paste0(dataPath,candidato,"/posts.csv"))
}

ExtraerDatosFacebook("hectorbaldassi", fbToken)
ExtraerDatosFacebook("martinllaryoraoficial", fbToken)
# ExtraerDatosFacebook("liliolivero", fbToken)
ExtraerDatosFacebook("pablocarrook", fbToken)
# ExtraerDatosFacebook("luciana-echevarría-253898394637965", fbToken)
# ExtraerDatosFacebook("eduardofernandez2017", fbToken)
# ExtraerDatosFacebook("253898394637965", fbToken)
# ExtraerDatosFacebook("dantevrossi", fbToken)