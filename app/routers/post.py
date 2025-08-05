from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy import func
from sqlalchemy.orm import Session 
from .. import models, schemas, oauth2
from ..database import get_db 

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)

# @router.get("/", response_model=list[schemas.PostResponse])
@router.get("/", )
async def Post(db: Session = Depends(get_db)):
    # posts = db.query(models.Posts).limit(limit).offset(skip).all()
    
    results = db.query(models.Posts, func.count(models.Vote.post_id).label("votes")).join(models.Vote,models.Vote.post_id == models.Posts.id, isouter=True).group_by(models.Posts.id).all()
    
    # results = db.query(    models.Posts.title,    func.count(models.Vote.post_id).label("votes")).outerjoin(    models.Vote, models.Vote.ost_id == models.Posts.id).group_by(    models.Posts.id).all()
    # print(results)
    posts_with_votes = [
        {**post.__dict__, "votes": votes}
        for post, votes in results
    ]

    return posts_with_votes


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_post(post: schemas.PostParams, db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    new_post = models.Posts(owner_id= current_user.user_id, **post.model_dump())
    print(current_user)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
#     cursor.execute("""INSERT INTO posts (title, content,published, id ) VALUES (%s, %s, %s,%s) RETURNING *""",
#                    (post.title, post.content, post.published, randrange(0, 1000000)))
#     new_post = cursor.fetchone()
#     conn.commit()
#     if not new_post:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST, detail="Post creation failed")
    return new_post


@router.get("/{id}", )
def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Posts).filter(models.Posts.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} you are looking for is not available")
    # cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id),))
    # post = cursor.fetchone()
    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Posts).filter(models.Posts.id == id)
    
    post = post_query.first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} you are trying to delete is not available")
    print(post.owner_id, type(post.owner_id))
    print(current_user.user_id, type(current_user.user_id))
    
    if str(post.owner_id) != str(current_user.user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")
        
    
    post_query.delete(synchronize_session=False)
    db.commit()
    # index = find_index_post(id)
    # my_posts.pop(index)
    return {"message": "Post deleted successfully"}


@router.put("/{id}", response_model=schemas.PostResponse)
def update_post(id: int, db: Session = Depends(get_db), post: schemas.PostParams = Body(...)):
    post_query = db.query(models.Posts).filter(models.Posts.id == id)

    if post_query.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} you are trying to update is not available")

    post_query.update(post.model_dump(), synchronize_session=False)
    db.commit()

    return {"message": {post_query.first()}}

