from loguru import logger
from sqlmodel import select
from app.dependencies import get_session

def init_defaults():
    # with next(get_session()) as session:

    #     roles_str = os.getenv("USER_ROLE", "")
    #     role_names = [role.strip() for role in roles_str.split(",") if role.strip()]
        
    #     for role_name in role_names:
    #         with session.no_autoflush:  
    #                 role_exists = session.exec(
    #                     select(Role).where(Role.role_name == role_name)
    #                 ).first()
            
    #                 if not role_exists:
    #                     new_role = Role(role_name=role_name)
    #                     session.add(new_role)
    #                     logger.info("Inserted ROLE in DB")
    #                 else:
    #                      logger.info("Defaults already seeded")
    #                      return "Defaults already seeded"
                    
    #     session.commit()
    logger.info("Initialize your defaults in this function.")
