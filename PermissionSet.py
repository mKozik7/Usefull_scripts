import boto3

def list_all_accounts():
    organizations = boto3.client('organizations')
    accounts = []
    next_token = ''
    while True:
        if next_token:
            response = organizations.list_accounts(NextToken=next_token)
        else:
            response = organizations.list_accounts()

        for account in response.get('Accounts', []):
            accounts.append(account['Id'])
        next_token = response.get('NextToken')
        if not next_token:
            break

    return accounts


def list_accounts_with_permission_set(instance_arn, permission_set_arn):
    sso_admin = boto3.client('sso-admin', region_name='eu-central-1')
    accounts_in_permission_set = []

    try:
        # Initialize the next token to None
        next_token = None

        # Use a loop to paginate through results
        while True:
            if next_token:
                # Call API with the next token for pagination
                response = sso_admin.list_accounts_for_provisioned_permission_set(
                    InstanceArn=instance_arn,
                    PermissionSetArn=permission_set_arn,
                    NextToken=next_token
                )
            else:
                # Initial call without next token
                response = sso_admin.list_accounts_for_provisioned_permission_set(
                    InstanceArn=instance_arn,
                    PermissionSetArn=permission_set_arn
                )
            
            # Append account IDs from the current page to the accounts list
            accounts_in_permission_set.extend(response.get('AccountIds', []))

            # Check if there is a NextToken, if not, break the loop
            next_token = response.get('NextToken')
            if not next_token:
                break

        if not accounts_in_permission_set:
            print("No accounts found with the specified permission set.")
        else:
            print(f"Found {len(accounts_in_permission_set)} accounts with the specified permission set.")
    
    except ClientError as e:
        print(f"An error occurred: {e}")
    
    return accounts_in_permission_set



def get_accounts_without_permission_set(instance_arn, permission_set_arn):
    all_accounts = list_all_accounts()
    accounts_with_permission_set = list_accounts_with_permission_set(instance_arn, permission_set_arn)

    accounts_without_permission_set = [account for account in all_accounts if account not in accounts_with_permission_set]

    return accounts_without_permission_set




def assign_permission_set(instance_arn, permission_set_arn, account_id, principal_type,principal_id):
    sso_admin = boto3.client('sso-admin', region_name='eu-central-1')

    sso_admin.create_account_assignment(
        InstanceArn=instance_arn,
        PermissionSetArn=permission_set_arn,
        PrincipalType=principal_type,   #group or user
        PrincipalId= principal_id,    #groupID   
        TargetId=account_id,
        TargetType='AWS_ACCOUNT'
    )



def delete_permission_set(instance_arn, permission_set_arn, account_id, principal_type,principal_id):
    sso_admin = boto3.client('sso-admin', region_name='eu-central-1')

    sso_admin.delete_account_assignment(
        InstanceArn=instance_arn,
        PermissionSetArn=permission_set_arn,
        PrincipalType=principal_type,
        PrincipalId= principal_id,       
        TargetId=account_id,
        TargetType='AWS_ACCOUNT'
    )





if __name__ == "__main__":
    instance_arn = "" #instance arn
    permission_set_arn = ""   # permission set arn 
    principal_id = "" #  (groupID)
    principal_type = "GROUP" # (GROUP or USER)
    
    accounts_to_provision = list_all_accounts()
    if accounts_to_provision:
        for account_id in accounts_to_provision:
            if account_id == '362107604147':
                continue
            assign_permission_set(instance_arn, permission_set_arn, account_id, principal_type,principal_id)
            print(f"Permission set assigned to account {account_id}")
    else:
        print("All accounts are associated with the permission set.")
