from provider.vpc.command import VpcOptions
from shared.common import *
from shared.error_handler import exception


class RDS(ResourceProvider):

    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    @exception
    def get_resources(self) -> List[Resource]:

        client = self.vpc_options.client('rds')

        resources_found = []

        response = client.describe_db_instances(Filters=[
            {'Name': 'engine',
             'Values': ['aurora', 'aurora-mysql', 'aurora-postgresql',
                        'mariadb', 'mysql', 'oracle-ee', 'oracle-se2',
                        'oracle-se1', 'oracle-se', 'postgres', 'sqlserver-ee',
                        'sqlserver-se', 'sqlserver-ex', 'sqlserver-web']
             }])

        message_handler("Collecting data from RDS Instances...", "HEADER")

        if len(response["DBInstances"]) > 0:

            for data in response["DBInstances"]:
                if data['DBSubnetGroup']['VpcId'] == self.vpc_options.vpc_id:
                    subnet_ids = []
                    for subnet in data['DBSubnetGroup']['Subnets']:
                        subnet_ids.append(subnet['SubnetIdentifier'])

                    resources_found.append(Resource(digest=ResourceDigest(id=data['DBInstanceArn'],
                                                                          type='aws_db_instance'),
                                                    name=data["DBInstanceIdentifier"],
                                                    details='DBInstance using subnets {} and engine {}'.format(
                                                        ', '.join(subnet_ids), data["Engine"]),
                                                    group='database'))

        return resources_found


class ELASTICACHE(ResourceProvider):

    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    @exception
    def get_resources(self) -> List[Resource]:

        client = self.vpc_options.client('elasticache')

        resources_found = []

        """ get all cache clusters """
        response = client.describe_cache_clusters()

        message_handler("Collecting data from Elasticache Clusters...", "HEADER")

        if len(response['CacheClusters']) > 0:

            """ iterate cache clusters to get subnet groups """
            for data in response['CacheClusters']:

                cachesubnet = client.describe_cache_subnet_groups(CacheSubnetGroupName=data['CacheSubnetGroupName'])

                if cachesubnet['CacheSubnetGroups'][0]['VpcId'] == self.vpc_options.vpc_id:
                    subnet_ids = []
                    for subnet in cachesubnet['CacheSubnetGroups'][0]['Subnets']:
                        subnet_ids.append(subnet['SubnetIdentifier'])

                    resources_found.append(Resource(digest=ResourceDigest(id=data['CacheClusterId'],
                                                                          type='aws_elasticache_cluster'),
                                                    name=data["CacheSubnetGroupName"],
                                                    details='Elasticache Cluster using subnets {} and engine {}'.format(
                                                        ', '.join(subnet_ids), data["Engine"]),
                                                    group='database'))

        return resources_found


class DOCUMENTDB(ResourceProvider):

    def __init__(self, vpc_options: VpcOptions):
        self.vpc_options = vpc_options

    @exception
    def get_resources(self) -> List[Resource]:

        client = self.vpc_options.client('docdb')

        resources_found = []

        response = client.describe_db_instances(Filters=[
            {'Name': 'engine',
             'Values': ['docdb']
             }])

        message_handler("Collecting data from DocumentDB Instances...", "HEADER")

        if len(response['DBInstances']) > 0:

            """ iterate cache clusters to get subnet groups """
            for data in response['DBInstances']:

                if data['DBSubnetGroup']['VpcId'] == self.vpc_options.vpc_id:
                    subnet_ids = []
                    for subnet in data['DBSubnetGroup']['Subnets']:
                        subnet_ids.append(subnet['SubnetIdentifier'])

                    resources_found.append(
                        Resource(digest=ResourceDigest(id=data['DBInstanceArn'], type='aws_docdb_cluster'),
                                 name=data["DBInstanceIdentifier"],
                                 details='Documentdb using subnets {} and engine {}'.format(', '.join(subnet_ids),
                                                                                            data["Engine"]),
                                 group='database'))

            return resources_found
