import graphene 
from graphql_auth.schema import UserQuery, MeQuery 
from graphql_auth import mutations

class AuthMutation(graphene.ObjectType):
    register = mutations.Register.Field())
    verify_account = mutations.VerifyAccount.Field()
    token_auth = mutations.ObtainJSONWebToken.Field() # For user login
    update_account = mutations.UpdateAccount.Field() # User update account functionality.  NOTE: Fontend requires user to auth self with JWT...UNLESS logged in as admin!  
    resend_activation_email = mutations.ResendActivationEmail.Field() # NOTE: In frontend DON"T USE success bool (superflous). Soley using errors will suffice.  
    send_password_reset_email = mutations.SendPasswordResetEmail.Field()
    password_reset = mutations.PasswordReset.Field() # Fontend requires old and new passwd along with jwt from email

class Query(UserQuery, MeQuery, graphene.ObjectType): 
    pass # Define tables

class Mutation(AuthMutation, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)
