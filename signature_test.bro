global n = 0;
global m = 0;
global p_num = 0;
global k = 0;

# 基本数据包
# A raw packet header, consisting of L2 header and everything in pkt_hdr. .
event raw_packet(p: raw_pkt_hdr){
    print "raw_packet!";
    print p;
    if(p?$l2){
        print p$l2;
    } else {
        print "no l2";
    }
    if(p?$ip){
        print p$ip;
    } else {
        print "no ip field";
    }
    if(p?$ip6){
        print p$ip6;
    } else {
        print "no ip6 field";
    }
    if(p?$tcp){
        print p$tcp;
    } else {
        print "no tcp field";
    }
    if(p?$udp){
        print p$udp;
    } else {
        print "no udp field";
    }
    if(p?$icmp){
        print p$icmp;
    } else {
        print "no icmp field";
    }
    p_num += 1;
}

event packet_contents(c: connection, contents: string){
    print "packet_contents!";
    # print c;
    # print contents;
    # p_num -= 1;
}

# phase-1-dump
event icmp_echo_request(C: connection, icmp: icmp_conn, id: count, seq: count, payload: string){
    print "icmp_echo_request!";
    print icmp;
    n += 1;
}

event icmp_echo_reply(C: connection, icmp: icmp_conn, id: count, seq: count, payload: string){
    print "icmp_echo_reply!";
    print icmp;
    m += 1;
}

event icmp_time_exceeded(C: connection, icmp: icmp_conn, code: count, context: icmp_context){
    print "icmp_time_exceeded!";
    k += 1;
}

event icmp_error_message(C: connection, icmp: icmp_conn, code: count, context: icmp_context){
    print "icmp_error_message!";
}

event icmp_neighbor_advertisement(C: connection, icmp: icmp_conn, router: bool, solicited: bool,
override: bool, tgt: addr, options: icmp6_nd_options){
    print "icmp_neighbor_advertisement!";
}

event icmp_neighbor_solicitation(C: connection, icmp: icmp_conn, tgt: addr, options: icmp6_nd_options){
    print "icmp_neighbor_solicitation!";
}

event icmp_packet_too_big(C: connection, icmp: icmp_conn, code: count, context: icmp_context){
    print "icmp_packet_too_big!";
}

event icmp_parameter_problem(C: connection, icmp: icmp_conn, code: count, context: icmp_context){
    print "icmp_parameter_problem!";
}

event icmp_redirect(C: connection, icmp: icmp_conn, tgt: addr, options: icmp6_nd_options){
    print "icmp_redirect!";
}

# phase-2-dump
# pm related
event pm_attempt_getport(r: connection, status: rpc_status, pr: pm_port_request){
    print "pm_attempt_getport!";
}

event pm_attempt_dump(r: connection, status: rpc_status){
    print "pm_attempt_dump!";
}

event pm_attempt_callit(r: connection, status: rpc_status, call: pm_callit_request){
    print "pm_attempt_callit!";
}

event pm_attempt_null(r: connection, status: rpc_status){
    print "pm_attempt_null!";
}

event pm_attempt_set(r: connection, status: rpc_status, m: pm_mapping){
    print "pm_attempt_set!";
}

event pm_attempt_unset(r: connection, status: rpc_status, m: pm_mapping){
    print "pm_attempt_unset!";
}

event pm_bad_port(r: connection, bad_p: count){
    print "pm_bad_port!";
}

event pm_request_callit(r: connection, call: pm_callit_request, p: port){
    print "pm_request_callit!";
}

event pm_request_dump(r: connection, m: pm_mappings){
    print "pm_request_dump!";
}

event pm_request_getport(r: connection, pr: pm_port_request, p: port){
    print "pm_request_getport!";
}

event pm_request_null(r: connection){
    print "pm_request_null!";
}

event pm_request_set(r: connection, m: pm_mapping, success: bool){
    print "pm_request_set!";
}

event pm_request_unset(r: connection, m: pm_mapping, success: bool){
    print "pm_request_unset!";
}

event rpc_call(C: connection, xid: count, prog: count, ver: count, proc: count, call_len: count){
    print "rpc_call!";
}

event rpc_dialogue(c: connection, prog: count, ver: count, proc: count, status: rpc_status, start_time: time, call_len: count, reply_len: count){
    print "rpc_dialogue!";
}

event rpc_reply(c: connection, xid: count, status: rpc_status, reply_len: count){
    print "rpc_reply!";
}

# phase-3-dump

# phase-4-dump

# phase-5-dump


event bro_init(){
    print "Let's start!";
}

event bro_done(){
    print "Over.";
    print n;
    print m;
    print k;
    print p_num;
}