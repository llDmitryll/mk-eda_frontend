module top( a, b, c, alpha, betta, gamma );
    input a, b, c;
    output alpha, betta, gamma;
    wire t;
    not( t, a );
    and ( betta, t, c );
    or ( gamma, t, b );
    xor ( alpha, betta, gamma );
endmodule
