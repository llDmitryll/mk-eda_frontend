module Mux(out, select, in0, in1);
    input in0, in1;
    input select;
    output out;
    assign out = select ? in1 : in0;
endmodule
