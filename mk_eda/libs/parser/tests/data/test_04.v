module ComplexLogicWithFeedback(A, B, C, Z);
    input A;
    input B;
    input C;
    output Z;
    wire notA, notB, notC, andAB, orBC, xorABnotC, feedback;
    not (notA, A);
    not (notB, B);
    not (notC, C);
    and (andAB, notA, notB);
    or (orBC, notB, notC);
    xor (xorABnotC, A, notC);
    and (feedback, xorABnotC, orBC);
    or (Z, feedback, andAB);
endmodule
