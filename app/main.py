from ldap3 import Server, Connection, ALL, ALL_ATTRIBUTES, SUBTREE,BASE, LEVEL
import pytz
from datetime import datetime
 
def main():
    host = 'ldap://eqa-uat-dir.nzqa.govt.nz'
    port = 389
    user = 'cn=admin,o=nzqa'
    pw = 'password'
    conn = connectToLdap(host,port,user,pw)
    now = pytz.utc.localize(datetime.now())

    # userId = input("enter userId : ")
    userId = "nzqaTPE174"
    userEntries = getUserEntries(conn,base='ou=Users2,o=dev',userId=userId)
    uid = userEntries[0]['uid']
    for entry in userEntries:
        userRoleDns = getRoleDns(conn,base=entry.entry_dn)
        userRoleAssociations = []
        roleMappings = []
        roles = []
        for userRoleDn in userRoleDns:
            roleDN = userRoleDn.entry_dn
            print()
            
            roleAssociationEntries = getRoleAssociation(conn,base=roleDN)
            roleAssociation = roleAssociationEntries[0]['attributes']['member'][0]
            startDate = roleAssociationEntries[0]['attributes']['startDate']
            endDate = roleAssociationEntries[0]['attributes'].get('endDate')
            if (endDate):
                if (startDate > now) or (endDate < now):
                    print(f"skipping roleDn: {roleDN} with startDate {startDate} and endDate {endDate}")
                    continue
            print()
            print(f" roleAssociation {roleAssociation}, startDate {startDate}, endDate {endDate}")
            roleMappingEntries = getRoleMapping(conn,base=roleAssociation) #[0]#['member']
            roleMapping = roleMappingEntries[0]['attributes']['member'][0] #.member
            print(f" roleMapping {roleMapping}")
            roleEntries = getRole(conn,base=roleMapping)
            role = roleEntries[0]['attributes']['cn'][0]
            print(f" role {role}")
            roleMappings.append(roleMapping)
            userRoleAssociations.append(roleAssociation)
            roles.append(role)
            # exit = input("press any key to continue")
            # if not exit:
            #     break
        
    #  return the results 
    print(f"ESAA user {userId} with uid {uid} has the following roleAssociations: \n{userRoleAssociations} \n and roleMappings: {roleMappings}\n and roles: {roles}")
    
def connectToLdap(host,port,user,pw) -> Connection : 
    ldapServer = Server(host=host, port=port, get_info=ALL)
    ldapConn = Connection(ldapServer, user=user, password=pw, auto_bind=True)
    return ldapConn

def getUserEntries(conn,base,userId) -> list : 
    conn.search(search_base=base, 
                # search_filter='(&(objectClass=Person)(groupMembership=*))', 
                # search_filter='(&(objectclass=eqaUser)(uid={0}*))',
                search_filter=f'(sia-userid={userId})',
                search_scope=SUBTREE, attributes=ALL_ATTRIBUTES)
    print(f"User search returned {len(conn.entries)} entries")
    return conn.entries

def getListOfUsers(conn,base) -> list : 
    conn.search(search_base=base, 
                search_filter='(sia-userid=*)',
                attributes=['groupMembership','uid','securityEquals'])
    print(f"User search returned {len(conn.entries)} entries")
    return conn.entries

def getRoleDns(conn,base) -> dict : 
    conn.search(search_base=base, 
                search_filter='(objectClass=eqaContext2)', 
                search_scope=SUBTREE, attributes=ALL_ATTRIBUTES)
    return conn.entries

def getRoleAssociation(conn,base) -> dict : 
    conn.search(search_base=base, 
                search_filter='(objectClass=eqaRoleAssociation2)', 
                search_scope=SUBTREE, attributes=ALL_ATTRIBUTES)
    return conn.response

def getRoleMapping(conn,base) -> dict : 
    conn.search(search_base=base, 
                search_filter='(objectClass=eqaRoleMapping2)', 
                search_scope=SUBTREE, attributes=ALL_ATTRIBUTES)
    return conn.response

def getRole(conn,base) -> dict : 
    conn.search(search_base=base, 
                search_filter='(objectClass=eqaRole2)', 
                search_scope=SUBTREE, attributes=ALL_ATTRIBUTES)
    return conn.response

def getGroupsDetails(conn,username,base):
    #  query for groups details
    conn.search(search_base=base, 
                search_filter='(cn='+username+')', 
                attributes=['cn','sn','givenName','fullName','ou','o'])
    print("Groups Details")
    print(conn.response)
    return conn.response

def getRolesDetails(conn,username,base):
    #  query for roles details
    conn.search(search_base=base, 
                search_filter='(cn='+username+')', 
                # all attributes 
                attributes=['cn','sn','givenName','fullName','ou','o'])
    print("Roles Details")
    print(conn.response)
    return conn.response

if __name__ == '__main__':
    main()