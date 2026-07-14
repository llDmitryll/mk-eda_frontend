module FullAdder(a, b, cin, sum, cout);
    input a, b, cin;
    output sum, cout;
    wire axb, aAndb, bAndcin, aAndcin;
    xor xor1(axb, a, b);
    xor xor2(sum, axb, cin);
    and and1(aAndb, a, b);
    and and2(bAndcin, b, cin);
    and and3(aAndcin, a, cin);
    or or1(cout, aAndb, bAndcin, aAndcin);
    assign out = sel[1] ? sel[0] ? in[3] : in[2] : sel[0] ? in[1] : in[0];
endmodule
