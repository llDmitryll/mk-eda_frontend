module mux4to1( out,  in,  sel);
    assign out = sel[1] ? sel[0] ? in[3] : in[2] : sel[0] ? in[1] : in[0];
endmodule
