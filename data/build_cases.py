"""
Generates cases.csv — 30 Packet Tracer / Cisco lab troubleshooting cases.
Run: python3 build_cases.py
Output: ../cases.csv
"""
import csv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

cases = [
# ---------------- VLAN (4) ----------------
dict(case_id="V01", category="VLAN", severity="High",
 symptom="PC-A (VLAN 10) cannot reach PC-B (VLAN 20) on the same switch, but both can ping their own gateway.",
 topology_note="SW1 trunk Gi0/1 to SW2. Access ports: Fa0/1=VLAN10, Fa0/2=VLAN20. L3 switch does inter-VLAN routing.",
 show_output="SW1# show interfaces trunk\nPort  Mode  Encapsulation  Status  Native vlan\nGi0/1 on    802.1q         trunking 1\nVlans allowed on trunk: 1,10\nVlans allowed and active in management domain: 1,10",
 expected_fault="Trunk not carrying VLAN 20 (switchport trunk allowed vlan missing 20)",
 osi_layer="Layer 2", concept_tag="trunk-allowed-vlan"),

dict(case_id="V02", category="VLAN", severity="Medium",
 symptom="New PC plugged into Fa0/5 gets an IP from DHCP but cannot reach anything, including its own gateway.",
 topology_note="Fa0/5 was previously used for a lab demo and never reset.",
 show_output="SW1# show interfaces fa0/5 switchport\nName: Fa0/5\nAdministrative Mode: static access\nOperational Mode: static access\nAccess Mode VLAN: 99 (VLAN0099)",
 expected_fault="Port assigned to wrong access VLAN (99 instead of intended 10)",
 osi_layer="Layer 2", concept_tag="access-vlan-mismatch"),

dict(case_id="V03", category="VLAN", severity="Low",
 symptom="Intermittent connectivity between SW1 and SW2, console shows repeated CDP native VLAN mismatch warnings.",
 topology_note="Trunk link Gi0/1 SW1 <-> Gi0/1 SW2.",
 show_output="%CDP-4-NATIVE_VLAN_MISMATCH: Native VLAN mismatch discovered on GigabitEthernet0/1 (1), with SW2 GigabitEthernet0/1 (99).\nSW1# show interfaces trunk\nPort  Native vlan\nGi0/1 1",
 expected_fault="Native VLAN mismatch across trunk (SW1=1, SW2=99)",
 osi_layer="Layer 2", concept_tag="native-vlan-mismatch"),

dict(case_id="V04", category="VLAN", severity="High",
 symptom="All PCs newly added to VLAN 30 cannot get an IP address or reach anything.",
 topology_note="VLAN 30 was planned for the new Finance department this week.",
 show_output="SW1# show vlan brief\nVLAN Name        Status    Ports\n1    default      active    Gi0/1\n10   Sales        active    Fa0/1\n20   Marketing    active    Fa0/2\n(VLAN 30 not listed)",
 expected_fault="VLAN 30 was never created in the VLAN database",
 osi_layer="Layer 2", concept_tag="missing-vlan"),

# ---------------- Gateway (4) ----------------
dict(case_id="G01", category="Gateway", severity="Medium",
 symptom="PC has a valid IP in 192.168.10.0/24 but cannot reach anything outside its subnet.",
 topology_note="Router G0/0.10 = 192.168.10.1.",
 show_output="PC> ipconfig\nIP Address: 192.168.10.55\nSubnet Mask: 255.255.255.0\nDefault Gateway: 192.168.10.100",
 expected_fault="Wrong default gateway configured on the PC (192.168.10.100 instead of .1)",
 osi_layer="Layer 3", concept_tag="wrong-default-gateway"),

dict(case_id="G02", category="Gateway", severity="High",
 symptom="All VLAN 20 users lost connectivity to the router at the same time this morning.",
 topology_note="Router-on-a-stick with sub-interfaces per VLAN.",
 show_output="R1# show ip interface brief\nInterface           IP-Address      Status                Protocol\nGigabitEthernet0/0.10 192.168.10.1   up                    up\nGigabitEthernet0/0.20 192.168.20.1   administratively down down",
 expected_fault="VLAN 20 sub-interface administratively shut down",
 osi_layer="Layer 3", concept_tag="subinterface-down"),

dict(case_id="G03", category="Gateway", severity="High",
 symptom="Half the LAN loses internet whenever R1 (the primary HSRP router) is powered off for maintenance, even though R2 is supposed to take over.",
 topology_note="R1 and R2 run HSRP group 1 for 192.168.1.1 virtual gateway.",
 show_output="R2# show standby brief\nInterface  Grp  Pri  P State   Active         Standby        Virtual IP\nGi0/1      1    90   Standby  R1(unreachable) local          192.168.1.1\nR1 priority was configured as 200, R2 as 90, preempt not enabled on R2",
 expected_fault="HSRP preempt not enabled on standby router, so it will not take over cleanly",
 osi_layer="Layer 3", concept_tag="hsrp-preempt"),

dict(case_id="G04", category="Gateway", severity="High",
 symptom="Entire VLAN 40 (new lab) cannot reach the gateway at all; ARP requests for .1 get no reply.",
 topology_note="L3 switch is supposed to route for VLAN 40 via SVI.",
 show_output="L3SW# show ip interface brief\nInterface  IP-Address      Status  Protocol\nVlan10     192.168.10.1    up      up\nVlan40     unassigned      up      up",
 expected_fault="No IP address configured on the VLAN 40 SVI",
 osi_layer="Layer 3", concept_tag="missing-svi-ip"),

# ---------------- DHCP (4) ----------------
dict(case_id="D01", category="DHCP", severity="High",
 symptom="All PCs on the remote VLAN 30 get a 169.254.x.x address instead of a DHCP-assigned one; DHCP server sits centrally on VLAN 1.",
 topology_note="Router routes between VLANs; DHCP server is a separate host on VLAN 1.",
 show_output="R1# show run interface g0/0.30\ninterface GigabitEthernet0/0.30\n encapsulation dot1Q 30\n ip address 192.168.30.1 255.255.255.0\n(no ip helper-address line present)",
 expected_fault="Missing 'ip helper-address' on the router interface for VLAN 30, so DHCP broadcasts never reach the server",
 osi_layer="Layer 3", concept_tag="dhcp-relay-missing"),

dict(case_id="D02", category="DHCP", severity="Medium",
 symptom="First 40 PCs in the lab got IP addresses fine this morning; PCs added after 9am get no address at all.",
 topology_note="DHCP pool configured for a /27 network (30 usable hosts).",
 show_output="R1# show ip dhcp pool LAN\nPool LAN :\n Leased addresses       30\n Excluded addresses     2\n High address           192.168.1.30\n Low address            192.168.1.2",
 expected_fault="DHCP pool address range exhausted (30 leased against a 30-host pool)",
 osi_layer="Layer 3", concept_tag="dhcp-pool-exhausted"),

dict(case_id="D03", category="DHCP", severity="Medium",
 symptom="Two devices on the network report the same IP address, one of them being the router's own gateway address.",
 topology_note="DHCP pool for 192.168.5.0/24, gateway is 192.168.5.1.",
 show_output="R1# show run | section dhcp\nip dhcp pool LAN\n network 192.168.5.0 255.255.255.0\n default-router 192.168.5.1\n(no ip dhcp excluded-address 192.168.5.1 line present)",
 expected_fault="Gateway address was never excluded from the DHCP pool, so it got leased to a client",
 osi_layer="Layer 3", concept_tag="dhcp-excluded-address-missing"),

dict(case_id="D04", category="DHCP", severity="Medium",
 symptom="New PCs get an IP address from DHCP but cannot ping the gateway or anything else.",
 topology_note="LAN is 192.168.8.0/24 (/24 mask), gateway 192.168.8.1.",
 show_output="PC> ipconfig\nIP Address: 192.168.8.50\nSubnet Mask: 255.255.255.240\nDefault Gateway: 192.168.8.1\nR1# show run | section dhcp\nip dhcp pool LAN\n network 192.168.8.0 255.255.255.240",
 expected_fault="DHCP pool configured with the wrong subnet mask (/28 instead of /24), placing gateway outside the client's calculated subnet",
 osi_layer="Layer 3", concept_tag="dhcp-wrong-mask"),

# ---------------- DNS (4) ----------------
dict(case_id="N01", category="DNS", severity="Medium",
 symptom="PC can successfully ping the server's IP address directly, but 'ping fileserver.local' fails with 'could not find host'.",
 topology_note="DHCP scope should hand out internal DNS server 192.168.1.53.",
 show_output="PC> ipconfig /all\nDNS Servers: 8.8.8.8\nR1# show run | section dhcp\nip dhcp pool LAN\n dns-server 8.8.8.8",
 expected_fault="Wrong DNS server address handed out by DHCP (public resolver instead of internal DNS at .53)",
 osi_layer="Layer 7", concept_tag="wrong-dns-server"),

dict(case_id="N02", category="DNS", severity="High",
 symptom="Every PC in the building suddenly cannot resolve any internal hostname; direct IP access still works fine.",
 topology_note="Single internal DNS server, no redundancy configured.",
 show_output="PC> nslookup fileserver.local\nDNS request timed out.\ntimeout was 2 seconds.\n*** Request to 192.168.1.53 timed-out\nDNS-SRV# show process (service not running / not reachable)",
 expected_fault="Internal DNS server service is down / unreachable",
 osi_layer="Layer 7", concept_tag="dns-server-down"),

dict(case_id="N03", category="DNS", severity="Low",
 symptom="PC can resolve 'fileserver.corp.local' when typed in full, but plain 'fileserver' fails.",
 topology_note="Correct DNS server is configured on the client.",
 show_output="PC> ipconfig /all\nDNS Servers: 192.168.1.53\nConnection-specific DNS Suffix: (none)",
 expected_fault="Missing DNS suffix on the client, so short (unqualified) names cannot be completed to an FQDN",
 osi_layer="Layer 7", concept_tag="missing-dns-suffix"),

dict(case_id="N04", category="DNS", severity="Medium",
 symptom="Laptop resolves external websites fine but cannot resolve any internal server name.",
 topology_note="Internal DNS is 192.168.1.53; the laptop was recently reconfigured with a static IP by mistake.",
 show_output="PC> ipconfig /all\nDNS Servers: 1.1.1.1\nDHCP Enabled: No",
 expected_fault="Client statically configured to use an external/ISP DNS resolver instead of the internal DNS server, so internal-only records cannot resolve",
 osi_layer="Layer 7", concept_tag="external-dns-misconfig"),

# ---------------- Routing (4) ----------------
dict(case_id="R01", category="Routing", severity="High",
 symptom="Branch office (10.20.0.0/24) can ping HQ servers, but HQ users cannot ping anything at the branch.",
 topology_note="HQ router R1, Branch router R2, static routing used end to end.",
 show_output="R1# show ip route\nGateway of last resort is not set\n     10.10.0.0/24 is directly connected, GigabitEthernet0/0\n(no route to 10.20.0.0/24 present)",
 expected_fault="Missing static route on HQ router (R1) back to the branch subnet 10.20.0.0/24",
 osi_layer="Layer 3", concept_tag="missing-static-route"),

dict(case_id="R02", category="Routing", severity="Medium",
 symptom="OSPF neighbor between R1 and R2 never reaches FULL state; it hangs at EXSTART/EXCHANGE.",
 topology_note="Both routers configured for OSPF area 0 on the link between them.",
 show_output="R1# show ip ospf neighbor\nNeighbor ID   Pri  State           Address\n2.2.2.2       1    EXSTART/  -      10.0.0.2\nR1 interface MTU: 1500   R2 interface MTU: 1400",
 expected_fault="MTU mismatch between R1 and R2 on the shared link, preventing OSPF database exchange from completing",
 osi_layer="Layer 3", concept_tag="ospf-mtu-mismatch"),

dict(case_id="R03", category="Routing", severity="Medium",
 symptom="Traffic to 172.16.30.0/24 is being sent out the wrong interface and never arrives.",
 topology_note="R1 has two WAN links: Se0/0/0 to ISP-A, Se0/0/1 to Branch.",
 show_output="R1# show run | include ip route\nip route 172.16.30.0 255.255.255.0 Serial0/0/0\n(172.16.30.0 is actually reachable via Serial0/0/1, the branch link)",
 expected_fault="Static route configured with the wrong exit interface/next hop",
 osi_layer="Layer 3", concept_tag="wrong-static-route-nexthop"),

dict(case_id="R04", category="Routing", severity="High",
 symptom="R1 and R2 are directly connected and both run EIGRP, but neither shows the other as a neighbor and no dynamic routes appear.",
 topology_note="Both routers were configured independently by different team members.",
 show_output="R1# show ip protocols\nRouting Protocol is \"eigrp 100\"\nR2# show ip protocols\nRouting Protocol is \"eigrp 200\"",
 expected_fault="EIGRP autonomous system numbers do not match between R1 (100) and R2 (200), so no neighbor relationship forms",
 osi_layer="Layer 3", concept_tag="eigrp-as-mismatch"),

# ---------------- ACL (4) ----------------
dict(case_id="A01", category="ACL", severity="High",
 symptom="Internal users cannot reach the web server on 192.168.100.10 over HTTP, even though the ACL is supposed to permit it.",
 topology_note="Extended ACL 101 applied inbound on the server-facing interface.",
 show_output="R1# show access-lists 101\nExtended IP access list 101\n 10 deny tcp any any eq 80\n 20 permit tcp any host 192.168.100.10 eq 80\n 30 permit ip any any",
 expected_fault="A deny statement for port 80 is listed above the intended permit, blocking the traffic due to first-match ACL processing",
 osi_layer="Layer 4", concept_tag="acl-statement-order"),

dict(case_id="A02", category="ACL", severity="Medium",
 symptom="PCs can send requests to the server but never receive any reply back.",
 topology_note="ACL 105 meant to filter inbound traffic on Gi0/1 toward the LAN.",
 show_output="R1# show ip interface gi0/1\n Outgoing access list is 105\n Inbound access list is not set",
 expected_fault="ACL applied in the outbound direction instead of inbound, blocking return traffic on the wrong pass",
 osi_layer="Layer 4", concept_tag="acl-wrong-direction"),

dict(case_id="A03", category="ACL", severity="Medium",
 symptom="After a routine ACL update, the entire 192.168.50.0/24 subnet lost access to every server, not just the one that was supposed to be restricted.",
 topology_note="Requirement was to block only 192.168.50.0/24 from reaching the HR server (192.168.100.20).",
 show_output="R1# show access-lists 10\nStandard IP access list 10\n 10 deny 192.168.50.0 0.0.0.255\n 20 permit any\napplied on interface toward HR server",
 expected_fault="A standard ACL (source-only filtering) was used where an extended ACL was required to match the specific destination, so all traffic from that subnet is blocked everywhere",
 osi_layer="Layer 3", concept_tag="standard-acl-misuse"),

dict(case_id="A04", category="ACL", severity="Low",
 symptom="New Finance subnet (192.168.60.0/24) added last week cannot reach the file server; older subnets work fine through the same ACL.",
 topology_note="ACL 110 was written before the Finance subnet existed.",
 show_output="R1# show access-lists 110\nExtended IP access list 110\n 10 permit ip 192.168.10.0 0.0.0.255 host 192.168.100.30\n 20 permit ip 192.168.20.0 0.0.0.255 host 192.168.100.30\n (implicit deny at end)",
 expected_fault="No explicit permit entry was added for the new Finance subnet, so it falls into the implicit deny at the end of the ACL",
 osi_layer="Layer 3", concept_tag="acl-implicit-deny"),

# ---------------- NAT (3) ----------------
dict(case_id="T01", category="NAT", severity="High",
 symptom="Internal PCs cannot reach the internet even though the ISP link is up and static routing looks correct.",
 topology_note="PAT overload configured on R1 for internet access.",
 show_output="R1# show ip nat translations\n(empty)\nR1# show run | include ip nat\nip nat inside source list 1 interface Gi0/0 overload\ninterface Gi0/1\n ip nat outside\n(Gi0/0, the LAN-facing interface, is missing 'ip nat inside')",
 expected_fault="'ip nat inside' was never applied to the internal interface, so no traffic is being marked for translation",
 osi_layer="Layer 3", concept_tag="nat-inside-missing"),

dict(case_id="T02", category="NAT", severity="High",
 symptom="External users report they cannot reach the company's public-facing web server at all.",
 topology_note="Static NAT maps public 203.0.113.10 to the internal web server.",
 show_output="R1# show run | include ip nat inside source static\nip nat inside source static 192.168.1.99 203.0.113.10\n(actual web server IP is 192.168.1.100, not .99)",
 expected_fault="Static NAT entry points to the wrong internal IP address (192.168.1.99 instead of the server's real address 192.168.1.100)",
 osi_layer="Layer 3", concept_tag="nat-static-wrong-ip"),

dict(case_id="T03", category="NAT", severity="Medium",
 symptom="Most of the office can browse the internet, but a handful of PCs on 192.168.1.192/27 cannot.",
 topology_note="NAT uses ACL 1 to define which hosts get translated.",
 show_output="R1# show access-lists 1\nStandard IP access list 1\n 10 permit 192.168.1.0 0.0.0.63\n(this ACL only covers 192.168.1.0-63, missing the .192/27 range)",
 expected_fault="The ACL feeding the NAT overload statement is too narrow and does not include the 192.168.1.192/27 range, so those hosts never get translated",
 osi_layer="Layer 3", concept_tag="nat-acl-too-narrow"),

# ---------------- Wireless (3) ----------------
dict(case_id="W01", category="Wireless", severity="High",
 symptom="Devices on the Guest Wi-Fi SSID can reach the internal file server, which should be isolated from guest traffic.",
 topology_note="Guest SSID maps to VLAN 90; internal server is on VLAN 10.",
 show_output="WLC# show wlan 2\nWLAN Profile Name: Guest\nInterface/Interface Group: management\n(Guest WLAN is mapped to the 'management' interface instead of a dedicated guest VLAN interface, and no ACL is applied)",
 expected_fault="Guest WLAN is not mapped to an isolated VLAN/interface and has no client-isolation ACL applied",
 osi_layer="Layer 2/3", concept_tag="guest-isolation-missing"),

dict(case_id="W02", category="Wireless", severity="Medium",
 symptom="Laptop repeatedly fails to authenticate to the office Wi-Fi despite the user re-typing the password carefully.",
 topology_note="AP configured for WPA2-PSK.",
 show_output="AP# show run | section wlan\nwlan OFFICE\n security wpa wpa2\n wpa-psk ascii 0 CorpWifi2024!\n(user's device is configured with passphrase 'CorpWiFi2024!' - case mismatch)",
 expected_fault="Pre-shared key mismatch between the AP configuration and the client (case-sensitive passphrase typed incorrectly on the device profile)",
 osi_layer="Layer 2", concept_tag="wpa-psk-mismatch"),

dict(case_id="W03", category="Wireless", severity="Low",
 symptom="Users near the east wall report frequent Wi-Fi drops and very slow speeds, though signal bars look full.",
 topology_note="Two APs (AP1, AP2) cover overlapping areas near the east wall.",
 show_output="AP1# show controllers dot11Radio 0 | include Channel\nChannel: 6\nAP2# show controllers dot11Radio 0 | include Channel\nChannel: 6\n(both APs on the same 2.4GHz channel, overlapping coverage)",
 expected_fault="Co-channel interference: AP1 and AP2 are set to the same 2.4GHz channel in overlapping coverage areas",
 osi_layer="Layer 1", concept_tag="channel-overlap"),
]

fieldnames = ["case_id","category","severity","symptom","topology_note","show_output","expected_fault","osi_layer","concept_tag"]

with open(PROJECT_ROOT / "cases.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    for c in cases:
        w.writerow(c)

print(f"Wrote {len(cases)} cases")
