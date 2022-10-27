from drf_spectacular.utils import OpenApiExample, extend_schema_view, extend_schema

POST_LIST_CATEGORY = [
    OpenApiExample(
        name="이것은 Select Parameter Example입니다.",
        summary="category=1, 자유게시판일 때",
        description="자유게시판일 경우",
        value=[
                    {
                        "category": "자유게시판",
                        "creator": "null",
                        "subject": "test1",
                        "content": "test1입니다",
                        "view": 2,
                        "recommend": 1,
                        "created_at": "2022-08-17T07:45:26.427319Z",
                        "postfile": [
                            {
                                "id": 1,
                                "file_url": "https://unsplash.com/photos/j7gxNfCIu1c",
                                "post": 1
                            }
                        ],
                        "reviewrating": []
                    },
            {
                        "category": "자유게시판",
                        "creator": "null",
                        "subject": "test3",
                        "content": "test3!",
                        "view": 0,
                        "recommend": 0,
                        "created_at": "2022-08-19T02:20:29.901195Z",
                        "postfile": [],
                        "reviewrating": []
                    },
            {
                        "category": "자유게시판",
                        "creator": {
                            "name": "superuser",
                            "email": "hh@email.com",
                            "nofilter_user_info": "null",
                            "is_active": "true"
                        },
                        "subject": "test4",
                        "content": "test4!",
                        "view": 0,
                        "recommend": 0,
                        "created_at": "2022-08-19T02:28:19.289491Z",
                        "postfile": [],
                        "reviewrating": []
                    },
            {
                        "category": "자유게시판",
                        "creator": {
                            "name": "박현희",
                            "email": "ahdzhd@naver.com",
                            "nofilter_user_info": {
                                "user": 8,
                                "nofilter_highschool": {
                                    "name": "상명고등학교",
                                    "location": "경북",
                                    "highschool_rating": []
                                },
                                "status": "학생",
                                "birthday": "2021-01-01"
                            },
                            "is_active": "true"
                        },
                        "subject": "h1",
                        "content": "h1 content",
                        "view": 0,
                        "recommend": 0,
                        "created_at": "2022-08-26T01:43:54.063257Z",
                        "postfile": [],
                        "reviewrating": []
                    },
            {
                        "category": "자유게시판",
                        "creator": {
                            "name": "박현희",
                            "email": "ahdzhd@naver.com",
                            "nofilter_user_info": {
                                "user": 8,
                                "nofilter_highschool": {
                                    "name": "상명고등학교",
                                    "location": "경북",
                                    "highschool_rating": []
                                },
                                "status": "학생",
                                "birthday": "2021-01-01"
                            },
                            "is_active": "true"
                        },
                        "subject": "testtest",
                        "content": "testtest!!",
                        "view": 0,
                        "recommend": 0,
                        "created_at": "2022-08-31T13:47:22.547941Z",
                        "postfile": [
                            {
                                "id": 43,
                                "file_url": "스크린샷 2022-08-29 오후 5.19.27.png",
                                "post": 49
                            },
                            {
                                "id": 44,
                                "file_url": "스크린샷 2022-08-22 오후 2.02.40.png",
                                "post": 49
                            }
                        ],
                        "reviewrating": []
                    },
            {
                        "category": "자유게시판",
                        "creator": {
                            "name": "박현희",
                            "email": "ahdzhd@naver.com",
                            "nofilter_user_info": {
                                "user": 8,
                                "nofilter_highschool": {
                                    "name": "상명고등학교",
                                    "location": "경북",
                                    "highschool_rating": []
                                },
                                "status": "학생",
                                "birthday": "2021-01-01"
                            },
                            "is_active": "true"
                        },
                        "subject": "testtest",
                        "content": "testtest!!",
                        "view": 0,
                        "recommend": 0,
                        "created_at": "2022-08-31T13:47:27.834100Z",
                        "postfile": [],
                        "reviewrating": []
                    }
        ]
    ),
    OpenApiExample(
        "이것은 Select Parameter Example2입니다.",
        summary="category=2, 리뷰게시판일 때",
        description="리뷰게시판",
        value=[
                    {
                        "category": "리뷰게시판",
                        "creator": {
                            "name": "박현희",
                            "email": "ahdzhd@naver.com",
                            "nofilter_user_info": {
                                "user": 8,
                                "nofilter_highschool": {
                                    "name": "상명고등학교",
                                    "location": "경북",
                                    "highschool_rating": []
                                },
                                "status": "학생",
                                "birthday": "2021-01-01"
                            },
                            "is_active": "true"
                        },
                        "subject": "testtest",
                        "content": "testtest!!",
                        "view": 0,
                        "recommend": 0,
                        "created_at": "2022-08-30T09:18:11.264429Z",
                        "postfile": [
                            {
                                "id": 39,
                                "file_url": "스크린샷 2022-08-29 오후 5.19.27.png",
                                "post": 47
                            },
                            {
                                "id": 40,
                                "file_url": "스크린샷 2022-08-22 오후 2.02.40.png",
                                "post": 47
                            }
                        ],
                        "reviewrating": [
                            {
                                "nofilter_highschool": 35,
                                "post": 47,
                                "item": "수업",
                                "rating": 5
                            },
                            {
                                "nofilter_highschool": 36,
                                "post": 47,
                                "item": "시설",
                                "rating": 4
                            }
                        ]
                    },
            {
                        "category": "리뷰게시판",
                        "creator": {
                            "name": "박현희",
                            "email": "ahdzhd@naver.com",
                            "nofilter_user_info": {
                                "user": 8,
                                "nofilter_highschool": {
                                    "name": "상명고등학교",
                                    "location": "경북",
                                    "highschool_rating": []
                                },
                                "status": "학생",
                                "birthday": "2021-01-01"
                            },
                            "is_active": "true"
                        },
                        "subject": "testtest",
                        "content": "testtest!!",
                        "view": 0,
                        "recommend": 0,
                        "created_at": "2022-08-30T09:18:23.401395Z",
                        "postfile": [
                            {
                                "id": 41,
                                "file_url": "스크린샷 2022-08-29 오후 5.19.27.png",
                                "post": 48
                            },
                            {
                                "id": 42,
                                "file_url": "스크린샷 2022-08-22 오후 2.02.40.png",
                                "post": 48
                            }
                        ],
                        "reviewrating": [
                            {
                                "nofilter_highschool": 37,
                                "post": 48,
                                "item": "수업",
                                "rating": 5
                            },
                            {
                                "nofilter_highschool": 38,
                                "post": 48,
                                "item": "시설",
                                "rating": 4
                            }
                        ]
                    }
        ],
    ),
]
