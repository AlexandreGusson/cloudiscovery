from typing import List

from shared.common import (
    ResourceProvider,
    Resource,
    BaseAwsOptions,
    ResourceDigest,
    message_handler,
    ResourceCache,
    LimitsValues,
)
from shared.error_handler import exception

ALLOWED_SERVICES_CODES = {
    "acm": {
        "L-F141DD1D": {
            "method": "list_certificates",
            "key": "CertificateSummaryList",
            "fields": [],
        },
        "global": False,
    },
    "amplify": {
        "L-1BED97F3": {"method": "list_apps", "key": "apps", "fields": [],},
        "global": False,
    },
    "codebuild": {
        "L-ACCF6C0D": {"method": "list_projects", "key": "projects", "fields": [],},
        "global": False,
    },
    "codecommit": {
        "L-81790602": {
            "method": "list_repositories",
            "key": "repositories",
            "fields": [],
        },
        "global": False,
    },
    "cloudformation": {
        "L-0485CB21": {"method": "list_stacks", "key": "StackSummaries", "fields": []},
        "global": False,
    },
    "ec2": {
        "L-0263D0A3": {
            "method": "describe_addresses",
            "key": "Addresses",
            "fields": [],
        },
        "global": False,
    },
    "elasticbeanstalk": {
        "L-8EFC1C51": {
            "method": "describe_environments",
            "key": "Environments",
            "fields": [],
        },
        "L-1CEABD17": {
            "method": "describe_applications",
            "key": "Applications",
            "fields": [],
        },
        "global": False,
    },
    "elasticloadbalancing": {
        "L-53DA6B97": {
            "method": "describe_load_balancers",
            "key": "LoadBalancers",
            "fields": [],
        },
        "global": False,
    },
    "iam": {
        "L-F4A5425F": {"method": "list_groups", "key": "Groups", "fields": [],},
        "L-F55AF5E4": {"method": "list_users", "key": "Users", "fields": [],},
        "L-BF35879D": {
            "method": "list_server_certificates",
            "key": "ServerCertificateMetadataList",
            "fields": [],
        },
        "L-6E65F664": {
            "method": "list_instance_profiles",
            "key": "InstanceProfiles",
            "fields": [],
        },
        "global": True,
    },
    "route53": {
        "L-4EA4796A": {
            "method": "list_hosted_zones",
            "key": "HostedZones",
            "fields": [],
        },
        "L-ACB674F3": {
            "method": "list_health_checks",
            "key": "HealthChecks",
            "fields": [],
        },
        "global": True,
    },
    "s3": {
        "L-DC2B2D3D": {"method": "list_buckets", "key": "Buckets", "fields": [],},
        "global": False,
    },
}


class LimitResources(ResourceProvider):
    def __init__(self, options: BaseAwsOptions):
        """
        All resources

        :param options:
        """
        super().__init__()
        self.options = options
        self.cache = ResourceCache()

    @exception
    # pylint: disable=too-many-locals
    def get_resources(self) -> List[Resource]:

        client_quota = self.options.session.client("service-quotas")

        resources_found = []

        services = self.options.services

        for service in services:
            cache_key = "aws_limits_" + service + "_" + self.options.region_name
            cache = self.cache.get_key(cache_key)

            for data_quota_code in cache[service]:
                quota_data = ALLOWED_SERVICES_CODES[service][
                    data_quota_code["quota_code"]
                ]

                value_aws = data_quota_code["value"]

                # Quota is adjustable by ticket request, then must override this values
                if bool(data_quota_code["adjustable"]) is True:
                    try:
                        response_quota = client_quota.get_service_quota(
                            ServiceCode=service, QuotaCode=data_quota_code["quota_code"]
                        )
                        if "Value" in response_quota["Quota"]:
                            value = response_quota["Quota"]["Value"]
                        else:
                            value = data_quota_code["value"]
                    except client_quota.exceptions.NoSuchResourceException:
                        value = data_quota_code["value"]

                message_handler(
                    "Collecting data from Quota: "
                    + service
                    + " - "
                    + data_quota_code["quota_name"]
                    + "...",
                    "HEADER",
                )

                """
                TODO: Add this as alias to convert service name
                """
                if service == "elasticloadbalancing":
                    service = "elbv2"

                client = self.options.session.client(
                    service, region_name=self.options.region_name
                )

                response = getattr(client, quota_data["method"])()

                usage = len(response[quota_data["key"]])

                percent = round((usage / value) * 100, 2)

                resources_found.append(
                    Resource(
                        digest=ResourceDigest(
                            id=data_quota_code["quota_code"], type="aws_limit"
                        ),
                        name="",
                        group="",
                        limits=LimitsValues(
                            quota_name=data_quota_code["quota_name"],
                            quota_code=data_quota_code["quota_code"],
                            aws_limit=int(value_aws),
                            local_limit=int(value),
                            usage=int(usage),
                            service=service,
                            percent=percent,
                        ),
                    )
                )

        return resources_found
