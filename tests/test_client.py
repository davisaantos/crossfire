from datetime import datetime, timedelta
from time import sleep
from unittest.mock import patch

from decouple import UndefinedValueError
from pytest import mark, raises

from crossfire.clients import (
    AsyncClient,
    Client,
    CredentialsNotFoundError,
    IncorrectCredentialsError,
    RetryAfterError,
    Token,
)
from crossfire.parser import UnknownFormatError


def test_client_initiates_with_proper_credentials(client):
    assert client.credentials["email"] == "email"
    assert client.credentials["password"] == "password"


def test_client_does_not_initiate_with_proper_credentials():
    with patch("crossfire.clients.config") as mock:
        mock.side_effect = UndefinedValueError()
        with raises(CredentialsNotFoundError):
            AsyncClient()


def test_client_initiates_with_credentials_from_kwargs():
    credentials_kwargs = {
        "email": "email.kwargs",
        "password": "password.kwargs",
    }
    client = AsyncClient(**credentials_kwargs)
    assert client.credentials["email"] == "email.kwargs"
    assert client.credentials["password"] == "password.kwargs"


@mark.asyncio
async def test_async_client_returns_a_token_when_cached_token_is_valid(
    client_with_token,
):
    assert await client_with_token.token() == "42"


@mark.asyncio
async def test_async_client_access_the_api_to_generate_token(
    token_client_and_post_mock,
):
    client, mock = token_client_and_post_mock
    await client.token()  # tries to access the API to get the token
    mock.assert_called_once_with(
        "http://127.0.0.1/api/v2/auth/login",
        json=client.credentials,
    )


@mark.asyncio
async def test_async_client_raises_an_error_with_wrong_credentials(
    client_and_post_mock,
):
    client, mock = client_and_post_mock
    client.cached_token = None
    mock.return_value.status_code = 401
    with raises(IncorrectCredentialsError):
        assert await client.token()


@mark.asyncio
async def test_async_client_requests_gets_new_token_from_api(
    token_client_and_post_mock,
):
    client, mock = token_client_and_post_mock
    mock.return_value.status_code = 201
    assert await client.token() == "forty-two"
    assert client.cached_token.valid_until <= datetime.now() + timedelta(
        seconds=3600
    )


@mark.asyncio
async def test_async_client_propagates_error_when_fails_to_get_token(
    client_and_post_mock,
):
    client, mock = client_and_post_mock
    mock.side_effect = Exception("Boom!")
    with raises(Exception) as error:
        await client.token()
        assert str(error.value) == "Boom!"


@mark.asyncio
async def test_async_client_goes_back_to_the_api_when_token_is_expired(
    token_client_and_post_mock,
):
    client, mock = token_client_and_post_mock
    client.cached_token = Token("42", -3600)
    await client.token()  # tries to access the API to get the token
    mock.assert_called_once_with(
        "http://127.0.0.1/api/v2/auth/login",
        json=client.credentials,
    )


@mark.asyncio
async def test_async_client_inserts_auth_header_on_http_get(
    client_and_get_mock,
):
    client, mock = client_and_get_mock
    await client.get("my-url")
    mock.assert_called_once_with(
        "my-url", headers={"Authorization": "Bearer 42"}
    )


@mark.asyncio
async def test_async_client_inserts_auth_on_http_get_without_overwriting(
    client_and_get_mock,
):
    client, mock = client_and_get_mock
    await client.get("my-url", headers={"answer": "forty-two"})
    mock.assert_called_once_with(
        "my-url", headers={"Authorization": "Bearer 42", "answer": "forty-two"}
    )


@mark.asyncio
async def test_async_client_raises_error_for_too_many_requests(
    client_and_get_mock,
):
    client, mock = client_and_get_mock
    mock.return_value.status_code = 429
    mock.return_value.headers = {"Retry-After": "42"}
    with raises(RetryAfterError):
        await client.get()


@mark.asyncio
async def test_async_client_load_states(state_client_and_get_mock):
    client, mock = state_client_and_get_mock
    states, metadata = await client.states()
    mock.assert_called_once_with(
        "http://127.0.0.1/api/v2/states",
        headers={"Authorization": "Bearer 42"},
    )
    assert len(states) == 1
    assert states[0]["name"] == "Rio de Janeiro"
    assert not metadata.page
    assert not metadata.take
    assert not metadata.item_count
    assert not metadata.page_count
    assert not metadata.has_previous_page
    assert not metadata.has_next_page


@mark.asyncio
async def test_async_client_load_states_as_df(state_client_and_get_mock):
    client, mock = state_client_and_get_mock
    states, _ = await client.states(format="df")
    mock.assert_called_once_with(
        "http://127.0.0.1/api/v2/states",
        headers={"Authorization": "Bearer 42"},
    )
    assert states.shape == (1, 2)
    assert states.name[0] == "Rio de Janeiro"


@mark.asyncio
async def test_async_client_load_states_raises_format_error(
    state_client_and_get_mock,
):
    client, _ = state_client_and_get_mock
    with raises(UnknownFormatError):
        await client.states(format="parquet")


@mark.asyncio
async def test_async_client_load_cities(city_client_and_get_mock):
    client, mock = city_client_and_get_mock
    cities, metadata = await client.cities()
    mock.assert_called_once_with(
        "http://127.0.0.1/api/v2/cities?",
        headers={"Authorization": "Bearer 42"},
    )
    assert cities[0]["name"] == "Rio de Janeiro"
    assert cities[0]["state"]["name"] == "Estado da Guanabara"
    assert not metadata.page
    assert not metadata.take
    assert not metadata.item_count
    assert not metadata.page_count
    assert not metadata.has_previous_page
    assert not metadata.has_next_page


@mark.asyncio
async def test_async_client_load_cities_as_dictionary(city_client_and_get_mock):
    client, mock = city_client_and_get_mock
    cities, _ = await client.cities(format="dict")
    mock.assert_called_once_with(
        "http://127.0.0.1/api/v2/cities?",
        headers={"Authorization": "Bearer 42"},
    )
    assert len(cities) == 1
    assert cities[0]["name"] == "Rio de Janeiro"
    assert cities[0]["state"]["name"] == "Estado da Guanabara"


@mark.asyncio
async def test_async_client_load_cities_with_city_id(city_client_and_get_mock):
    client, mock = city_client_and_get_mock
    await client.cities(city_id="21")
    mock.assert_called_once_with(
        "http://127.0.0.1/api/v2/cities?cityId=21",
        headers={"Authorization": "Bearer 42"},
    )


@mark.asyncio
async def test_async_client_with_city_name(city_client_and_get_mock):
    client, mock = city_client_and_get_mock
    await client.cities(city_name="Rio de Janeiro")
    mock.assert_called_once_with(
        "http://127.0.0.1/api/v2/cities?cityName=Rio+de+Janeiro",
        headers={"Authorization": "Bearer 42"},
    )


@mark.asyncio
async def test_async_client_load_cities_with_state_id(city_client_and_get_mock):
    client, mock = city_client_and_get_mock
    await client.cities(state_id="42")
    mock.assert_called_once_with(
        "http://127.0.0.1/api/v2/cities?stateId=42",
        headers={"Authorization": "Bearer 42"},
    )


@mark.asyncio
async def test_async_client_load_cities_with_more_than_one_params(
    city_client_and_get_mock,
):
    client, mock = city_client_and_get_mock
    await client.cities(state_id="42", city_name="Rio de Janeiro")
    mock.assert_called_once_with(
        "http://127.0.0.1/api/v2/cities?cityName=Rio+de+Janeiro&stateId=42",
        headers={"Authorization": "Bearer 42"},
    )


@mark.asyncio
async def test_async_client_occurrences(occurrences_client_and_get_mock):
    client, mock = occurrences_client_and_get_mock
    await client.occurrences(42)
    mock.assert_called_once_with(
        "http://127.0.0.1/api/v2/occurrences?idState=42&typeOccurrence=all&page=1",
        headers={"Authorization": "Bearer 42"},
    )


@mark.asyncio
async def test_client_runs_when_async_loop_is_running():
    # first let's set an async task to be running in parallel
    done = False

    async def async_task():
        while not done:
            sleep(0.1)

    task = async_task()

    # with some async task running, let's run our client, which that requires an
    # async loop
    with patch("crossfire.clients.config") as config_mock:
        with patch.object(AsyncClient, "states") as async_states_mock:
            config_mock.side_effect = ("email", "password")
            async_states_mock.return_value = ("forty-two", 42)
            client = Client()
            client.states(format=None)
            async_states_mock.assert_called_with(format=None)

    # finally, lets tear down our dummy async task
    done = True
    await task


def test_client_load_states():
    with patch("crossfire.clients.config") as config_mock:
        with patch.object(AsyncClient, "states") as async_states_mock:
            config_mock.side_effect = ("email", "password")
            async_states_mock.return_value = ("forty-two", 42)
            client = Client()
            client.states(format=None)
            async_states_mock.assert_called_with(format=None)


def test_client_load_cities():
    with patch("crossfire.clients.config") as config_mock:
        with patch.object(AsyncClient, "cities") as async_cities_mock:
            config_mock.side_effect = ("email", "password")
            async_cities_mock.return_value = ("forty-two", 42)
            client = Client()
            client.cities(
                city_id=42,
                city_name="Forty-two",
                state_id=42,
                format="Forty-Two",
            )
            async_cities_mock.assert_called_with(
                city_id=42,
                city_name="Forty-two",
                state_id=42,
                format="Forty-Two",
            )


def test_client_load_occurrences():
    with patch("crossfire.clients.config") as config_mock:
        with patch.object(AsyncClient, "occurrences") as async_occurrences_mock:
            config_mock.side_effect = ("email", "password")
            client = Client()
            client.occurrences(
                id_state=42,
                id_cities=42,
                type_occurrence="all",
                initial_date=None,
                final_date=None,
                max_parallel_requests=None,
                format=None,
            )
            async_occurrences_mock.assert_called_with(
                id_state=42,
                id_cities=42,
                type_occurrence="all",
                initial_date=None,
                final_date=None,
                max_parallel_requests=None,
                format=None,
            )
