import io

from rest_framework import parsers, renderers
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.compat import coreapi, coreschema
from rest_framework.schemas import ManualSchema
from rest_framework.authtoken.models import Token
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers.account import RegisterSerializer

from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt


class CreateAccountView(APIView):

    @csrf_exempt
    def post(self, request):
        """
        For creating accounts
        - Will be replaced by OAuth
        - does not validate login info such as password complexity

        Returns token for user

        """
        # Loading data
        stream = io.BytesIO(request.body)
        data = JSONParser().parse(stream)

        serializer = RegisterSerializer(data=data)

        if serializer.is_valid():

            # creating user
            user, created = User.objects.get_or_create(
                username=data.get("username"),
            )
            user.set_password(data.get("password"))
            user.save()

            # creating token
            token, _ = Token.objects.get_or_create(user=user)

            # returning id to user
            return Response({"token": token.key}, status=201)
        else:
            return Response(serializer.errors, status=400)


class ObtainAuthToken(APIView):
    """
    Stolen from django restframework, I added the "id" field of the users profile
    """
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = AuthTokenSerializer
    if coreapi is not None and coreschema is not None:
        schema = ManualSchema(
            fields=[
                coreapi.Field(
                    name="username",
                    required=True,
                    location='form',
                    schema=coreschema.String(
                        title="Username",
                        description="Valid username for authentication",
                    ),
                ),
                coreapi.Field(
                    name="password",
                    required=True,
                    location='form',
                    schema=coreschema.String(
                        title="Password",
                        description="Valid password for authentication",
                    ),
                ),
            ],
            encoding="application/json",
        )

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # getting token
        token, created = Token.objects.get_or_create(user=user)

        response = {'token': token.key}

        return Response(response)
