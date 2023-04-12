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

    # users = getListOfUsers(conn,base='ou=Users2,o=dev')
    # for user in users:
    #     print(user)
    #     userId = user
    #     break

    # userId = input("enter userId : ")
    userId = "nzqaTPE174"
    userEntries = getUserEntries(conn,base='ou=Users2,o=dev',userId=userId)
    
    uid = userEntries[0]['uid']
    for entry in userEntries: # should only be one - need to warn when not
        eqaContexts = getRoleDns(conn,base=entry.entry_dn)
        
        roles = set()
        for eqaContext in eqaContexts:
            roleDN = eqaContext.entry_dn
            roleAssociations = getRoleAssociation(conn,base=roleDN)
            
            roleAssociation = roleAssociations[0]['attributes']['member'][0]
            startDate = roleAssociations[0]['attributes']['startDate']
            endDate = roleAssociations[0]['attributes'].get('endDate')
            if (endDate):
                if (startDate > now) or (endDate < now):
                    print(f"skipping roleDn: {roleDN} with startDate {startDate} and endDate {endDate}")
                    continue
            roleMappings = getRoleMapping(conn,base=roleAssociation) 
            
            roleMapping = roleMappings[0]['attributes']['member'][0]
            mappedRoles = getRole(conn,base=roleMapping)
            role = mappedRoles[0]['attributes']['cn'][0]

            roles.add(role)
        
    #  return the results 
    print(f"ESAA user {userId} with uid {uid} has the following roles: ")
    for r in roles:
        print(f" - {r}")
    
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
                search_scope=SUBTREE, attributes=ALL_ATTRIBUTES)
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

if __name__ == '__main__':
    main()