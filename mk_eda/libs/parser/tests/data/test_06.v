module ComplexLogic(A, B, C, Z);
    input A;
    input B;
    input C;
    output Z;
    wire andAB, orBC, notC, xorAnotC;
    and (andAB, A, B);
    or (orBC, B, C);
    not (notC, C);
    xor (xorAnotC, A, notC);
    and (Z, andAB, orBC, xorAnotC);
endmodule
