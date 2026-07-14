module test_02(a,b,c);

    input a,b;
    output c;

    wire t;

    not(t,a);
    and(c,t,b);

endmodule
