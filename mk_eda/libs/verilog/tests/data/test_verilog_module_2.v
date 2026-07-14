module Top(a, b, c, o);
    input a;
    input b;
    input c;
    output o;
    wire d, e, f, g;
    and (d, a, b);
    xor (e, a, b);
    or (f, d, e);
    and (g, b, c);
    xnor (o, f, g);
endmodule
