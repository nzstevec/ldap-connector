from ldap3 import Server, Connection, ALL, ALL_ATTRIBUTES, SUBTREE,BASE, LEVEL
import pytz
from datetime import datetime
from ast import literal_eval
 
def main():
    host = 'ldap://eqa-uat-dir.nzqa.govt.nz'
    port = 389
    user = 'cn=admin,o=nzqa'
    pw = 'password'
    conn = connectToLdap(host,port,user,pw)
    now = pytz.utc.localize(datetime.now())
    base = 'ou=Users2,o=dev'

    userIds = set()
    users = getListOfUsers(conn,base)
    for user in users:
        userId = getattr(user,'sia-userid')
        if userId:
            userIds.add(str(userId))

    # userId = input("enter userId : ")
    userId = "nzqaTPE174"
    for userId in ["nzqaTPE174"]:
    # for userId in userIds:
        userEntries = getUserEntries(conn,base,userId=userId)
        if not userEntries:
            continue
        if len(userEntries) > 1:
            print(f"***** WARNING - duplicated userEntries, num = {len(userEntries)}")
        uid = userEntries[0]['uid']
        userLocationAccessRights = set()
        user_perorg_ids = set()
        locationCount = 0
        expiredCount = 0
        skipped = []
        entry = userEntries.pop()
        # for entry in userEntries: # should only be one - need to warn when not
        # print(f"line 31 entry = {entry}")
        eqaContexts = getRoleDns(conn,base=entry.entry_dn)
        locationCount = len(eqaContexts)

        for eqaContext in eqaContexts:
            contextRefId = eqaContext.contextRefId
            # print(f"processing {contextRefId}")
            locationAccessRights = []
            roleDN = eqaContext.entry_dn
            roleAssociations = getRoleAssociation(conn,base=roleDN)
            
            if not roleAssociations:
                continue
            roleAssociationAttrs = roleAssociations.pop().entry_attributes_as_dict
            roleAssociationMember = roleAssociationAttrs['member'][0]
            startDate = roleAssociationAttrs.get('startDate')
            if startDate:
                startDate = startDate[0]
            endDate = roleAssociationAttrs.get('endDate')
            if endDate:
                endDate = endDate[0]
            if not (startDate or endDate):
                continue
            if (startDate and endDate):
                # print(f"checking start/end date for roleDn: {roleDN} with startDate {startDate} and endDate {endDate}")
                if (now < startDate) or (now > endDate):
                    skipped.append(f"skipping roleDn: {roleDN} with startDate {startDate} and endDate {endDate}")
                    expiredCount += 1
                    continue
            elif startDate:
                # print(f"checking start date for roleDn: {roleDN} with startDate {startDate}")
                if now < startDate:
                    skipped.append(f"skipping roleDn: {roleDN} with startDate {startDate}")
                    expiredCount += 1
                    continue
            roleMappings = getRoleMapping(conn,base=roleAssociationMember) 
            if not roleMappings:
                continue
            roleMappingAttrs = roleMappings.pop().entry_attributes_as_dict
            for roleMapping in roleMappingAttrs.get('member'):
                mappedRoles = getRole(conn,base=roleMapping)
                if not mappedRoles:
                    continue
                mappedRolesAttrs = mappedRoles.pop().entry_attributes_as_dict
                roleMembers = mappedRolesAttrs.get('member')
                if not roleMembers:
                    continue
                for roleMember in roleMembers:
                    accessRights = getAccessRight(conn,base=roleMember)
                    locationAccessRights.append(accessRights.pop().entry_attributes_as_dict['cn'][0])
                if len(locationAccessRights) > 0:
                    userLocationAccessRights.add(str((contextRefId,locationAccessRights)))
                    user_perorg_ids.add(str(contextRefId))
        
        if len(userLocationAccessRights) == 0:
            continue    
        #  return the results 
        print(f"ESAA user {userId} with uid {uid} has {locationCount} locations in LDAP with {expiredCount} expired leaving the following {len(userLocationAccessRights)} location based access rights: ")
        print()
        for rights in userLocationAccessRights:
            print(rights)
        print()
        for skip in skipped:
            print(skip)
        print()
        print(f"provider_id (aka perorg_id) list = {tuple(literal_eval(str(user_perorg_ids)))}")
        
    
def connectToLdap(host,port,user,pw) -> Connection : 
    ldapServer = Server(host=host, port=port, get_info=ALL)
    ldapConn = Connection(ldapServer, user=user, password=pw, auto_bind=True)
    return ldapConn

def getUserEntries(conn,base,userId) -> list : 
    return search(conn, base, f'(&(sia-userid={userId})(uid=*))')

def getListOfUsers(conn,base) -> list : 
    return search(conn, base, '(sia-userid=*)')

def getRoleDns(conn,base) -> dict : 
    return search(conn, base, '(&(objectClass=eqaContext2)(contextRefId=*))')

def getRoleAssociation(conn,base) -> dict : 
    return search(conn, base, '(&(objectClass=eqaRoleAssociation2)(member=*))')

def getRoleMapping(conn,base) -> dict : 
    return search(conn, base, '(&(objectClass=eqaRoleMapping2)(member=*))') 

def getRole(conn,base) -> dict : 
    return search(conn, base, '(&(objectClass=eqaRole2)(member=*))')

def getAccessRight(conn,base) -> dict : 
    return search(conn, base, '(objectClass=eqaAccessRight2)')

def search(conn, base, filter):
    conn.search(search_base=base, 
                search_filter=filter, 
                search_scope=SUBTREE, attributes=ALL_ATTRIBUTES)
    return conn.entries

if __name__ == '__main__':
    main()