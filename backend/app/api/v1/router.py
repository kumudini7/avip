from fastapi import APIRouter

from app.api.v1.endpoints import (
    admin_assessments,
    analysis,
    assessments,
    auth,
    demo,
    documents,
    domains,
    gtm,
    health,
    projects,
    proposals,
    questions,
    use_cases,
)


api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(demo.router, prefix="/demo", tags=["demo"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(documents.router, prefix="/projects", tags=["documents"])
api_router.include_router(analysis.router, prefix="/projects", tags=["analysis"])
api_router.include_router(proposals.router, prefix="/projects", tags=["proposals"])
api_router.include_router(gtm.router, prefix="/gtm", tags=["gtm"])
api_router.include_router(domains.router, prefix="/domains", tags=["domains"])
api_router.include_router(questions.router, prefix="/questions", tags=["questions"])
api_router.include_router(assessments.router, prefix="/assessments", tags=["assessments"])
api_router.include_router(admin_assessments.router, prefix="/admin", tags=["admin-assessments"])
api_router.include_router(use_cases.router, prefix="/gtm/use-cases", tags=["use-cases"])
