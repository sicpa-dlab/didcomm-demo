import click
from didcomm.errors import DIDCommError
from didcomm.pack_encrypted import PackEncryptedConfig
from didcomm.secrets.secrets_resolver_demo import SecretsResolverDemo
from peerdid.errors import MalformedPeerDIDError
from peerdid.types import VerificationMaterialFormatPeerDID

from didcomm_demo.didcomm_demo import DIDCommDemo

secrets_resolver = SecretsResolverDemo()


def set_secrets_resolver(resolver: SecretsResolverDemo):
    global secrets_resolver
    secrets_resolver = resolver


@click.group()
def cli():
    pass


@cli.command()
@click.option('--auth-keys-count', default=1, help='Number of authentication keys')
@click.option('--agreement-keys-count', default=1, help='Number of agreement keys')
@click.option('--service-endpoint', default=None, help='Optional service endpoint')
@click.option('--service-routing-key', default=[], multiple=True, help='Optional service routing keys')
def create_peer_did(auth_keys_count, agreement_keys_count, service_endpoint, service_routing_key):
    click.echo()
    demo = DIDCommDemo(secrets_resolver)
    try:
        did = demo.create_peer_did(
            auth_keys_count=auth_keys_count,
            agreement_keys_count=agreement_keys_count,
            service_endpoint=service_endpoint,
            service_routing_keys=service_routing_key
        )
        click.echo(f"{did}")
    except (ValueError, TypeError) as e:
        click.echo(f"{e}")
    click.echo()


@cli.command()
@click.argument('did')
@click.option('--format', type=click.Choice(['jwk', 'multibase'], case_sensitive=False),
              default="jwk",
              help='DID Doc format (JWK or Multibase)')
def resolve_peer_did(did, format):
    click.echo()
    format = VerificationMaterialFormatPeerDID.JWK if format == "jwk" else VerificationMaterialFormatPeerDID.MULTIBASE
    try:
        did_doc_json = DIDCommDemo.resolve_peer_did(did, format)
        click.echo(f"{did_doc_json}")
    except MalformedPeerDIDError as e:
        click.echo(f"{e}")
    click.echo()


@cli.command()
@click.argument('msg')
@click.option('--to', required=True, help="Receiver's DID")
@click.option('--from', 'frm', default=None, help="Sender's DID. Anonymous encryption is used if not set.")
@click.option('--sign-from', default=None,
              help="Sender's DID for optional signing. The message is not signed if not set.")
@click.option('--protect-sender-id', default=True,
              help="Whether the sender's ID (DID) must be hidden. True by default.")
def pack(msg, to, frm, sign_from, protect_sender_id):
    click.echo()
    demo = DIDCommDemo(secrets_resolver)
    try:
        res = demo.pack(
            msg=msg,
            to=to,
            frm=frm,
            sign_frm=sign_from,
            config=PackEncryptedConfig(protect_sender_id=protect_sender_id)
        )
        click.echo(f"{res.packed_msg}")
    except DIDCommError as e:
        click.echo(f"{e}")
    click.echo()


@cli.command()
@click.argument('msg')
def unpack(msg):
    click.echo()
    try:
        demo = DIDCommDemo(secrets_resolver)
        initial_msg, frm, to, _ = demo.unpack(msg)
        click.echo()
        if frm:
            click.echo(f"authcrypted {initial_msg} from {frm} to {to}")
        else:
            click.echo(f"anoncrypted {initial_msg} to {to}")
    except DIDCommError as e:
        click.echo(f"{e}")
    click.echo()


if __name__ == '__main__':
    cli()
