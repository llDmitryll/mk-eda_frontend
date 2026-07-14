module test_03(input a,b,c, output d);

    wire t1,t2,t3;

    not(t1,a);
    and(t2,t1,b);
    not(t3,t2);
    and(d,t3,t1,t2,c);

endmodule
