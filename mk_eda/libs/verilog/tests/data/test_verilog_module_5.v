module RegisterFile(read_data, clk, write_enable, write_data, address);
    input clk, write_enable;
    input [3:0] write_data;
    input [1:0] address;
    output [3:0] read_data;
    reg [3:0] registers;
endmodule
