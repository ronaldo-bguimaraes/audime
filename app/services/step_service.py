"""Helper functions to manage extraction pipeline steps (checklist)."""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from abstract.models.core import ExtracaoStep, PipelineStep, StepStatus

STEP_ORDER = {
    PipelineStep.RAW_IMPORT: 1,
    PipelineStep.STAGING: 2,
    PipelineStep.ANALYTICS: 3,
    PipelineStep.COMPLETE: 4,
}


def init_steps(db: Session, id_extracao: int) -> list[ExtracaoStep]:
    """Create all 4 pipeline steps for an extraction in PENDING state."""
    steps = []
    for etapa in PipelineStep:
        step = ExtracaoStep(
            id_extracao=id_extracao,
            etapa=etapa,
            status=StepStatus.PENDING,
            ordem=STEP_ORDER[etapa],
        )
        db.add(step)
        steps.append(step)
    db.commit()
    for s in steps:
        db.refresh(s)
    return steps


def set_step_running(db: Session, id_extracao: int, etapa: PipelineStep) -> ExtracaoStep:
    """Mark a pipeline step as RUNNING."""
    step = _get_step(db, id_extracao, etapa)
    step.status = StepStatus.RUNNING
    step.iniciado_em = datetime.now(timezone.utc)
    db.commit()
    return step


def set_step_done(db: Session, id_extracao: int, etapa: PipelineStep) -> ExtracaoStep:
    """Mark a pipeline step as DONE."""
    step = _get_step(db, id_extracao, etapa)
    step.status = StepStatus.DONE
    step.concluido_em = datetime.now(timezone.utc)
    if not step.iniciado_em:
        step.iniciado_em = step.concluido_em
    db.commit()
    return step


def set_step_error(db: Session, id_extracao: int, etapa: PipelineStep, message: str = "") -> ExtracaoStep:
    """Mark a pipeline step as ERROR."""
    step = _get_step(db, id_extracao, etapa)
    step.status = StepStatus.ERROR
    step.concluido_em = datetime.now(timezone.utc)
    if not step.iniciado_em:
        step.iniciado_em = step.concluido_em
    step.mensagem = message
    db.commit()
    return step


def reset_steps(db: Session, id_extracao: int) -> None:
    """Reset all steps to PENDING (for reprocess)."""
    steps = (
        db.query(ExtracaoStep)
        .filter(ExtracaoStep.id_extracao == id_extracao)
        .all()
    )
    for s in steps:
        s.status = StepStatus.PENDING
        s.iniciado_em = None
        s.concluido_em = None
        s.mensagem = None
    db.commit()


def _get_step(db: Session, id_extracao: int, etapa: PipelineStep) -> ExtracaoStep:
    step = (
        db.query(ExtracaoStep)
        .filter(
            ExtracaoStep.id_extracao == id_extracao,
            ExtracaoStep.etapa == etapa,
        )
        .first()
    )
    if not step:
        step = ExtracaoStep(
            id_extracao=id_extracao,
            etapa=etapa,
            status=StepStatus.PENDING,
            ordem=STEP_ORDER[etapa],
        )
        db.add(step)
        db.commit()
        db.refresh(step)
    return step
