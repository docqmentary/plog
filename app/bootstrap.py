from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from sqlmodel import select

from .db import session_scope
from .models import Blog, BlogStatus, BlogVerification, KeywordVolume, Post, RefCardMyBlog, User

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def bootstrap_sample_data() -> None:
    with session_scope() as session:
        user = session.exec(select(User).where(User.email == "dev@example.com")).first()
        if not user:
            user = User(google_sub="dev-sub", email="dev@example.com", display_name="Dev User")
            session.add(user)
            session.flush()

        blog = session.exec(select(Blog).where(Blog.owner_user_id == user.id)).first()
        if not blog:
            blog = Blog(owner_user_id=user.id, naver_blog_id="myblog", title="내 클리닉 블로그", status=BlogStatus.VERIFIED)
            session.add(blog)
            session.flush()
            verification = BlogVerification(
                blog_id=blog.id,
                title_token="verify-title-token",
                body_token="verify-body-token",
                post_url="https://blog.naver.com/myblog/verify",
                verified_at=datetime.utcnow(),
            )
            session.add(verification)

        posts = session.exec(select(Post).where(Post.blog_id == blog.id)).all()
        if not posts:
            sample_csv = DATA_DIR / "sample_posts.csv"
            if sample_csv.exists():
                with sample_csv.open() as fp:
                    reader = csv.DictReader(fp)
                    for row in reader:
                        post = Post(
                            blog_id=blog.id,
                            url=row["url"],
                            main_keyword=row.get("main_keyword"),
                            expected_rank_at_publish=int(row["expected_rank_at_publish"]) if row.get("expected_rank_at_publish") else None,
                        )
                        session.add(post)
                        session.flush()
                        my_card = RefCardMyBlog(
                            post_id=post.id,
                            url=post.url,
                            title=f"{post.main_keyword} 경험담",
                            summary="내원 환자 케이스 기반 톤",
                            postdate=row.get("published_at"),
                        )
                        session.add(my_card)

        seed_volumes = {"환절기 아토피": 12800, "아토피 보습": 8200}
        for keyword, volume in seed_volumes.items():
            existing = session.exec(
                select(KeywordVolume).where(KeywordVolume.keyword == keyword).order_by(KeywordVolume.month.desc())
            ).first()
            if not existing:
                session.add(
                    KeywordVolume(
                        keyword=keyword,
                        month=datetime.utcnow().strftime("%Y-%m"),
                        volume_total=volume,
                    )
                )


__all__ = ["bootstrap_sample_data"]
