   -- this function converts a given string to std-logic-vector.
   function to_std_logic(c: character) return std_logic is 
       variable sl: std_logic;
       begin
          case c is
            when 'U' => 
               sl := 'U'; 
            when 'X' =>
               sl := 'X';
            when '0' => 
               sl := '0';
            when '1' => 
               sl := '1';
            when 'Z' => 
               sl := 'Z';
            when 'W' => 
               sl := 'W';
            when 'L' => 
               sl := 'L';
            when 'H' => 
               sl := 'H';
            when '-' => 
               sl := '-';
            when others =>
               sl := 'X'; 
        end case;
        return sl;
    end to_std_logic;

    -- converts a string into std_logic_vector
    function to_std_logic_vector(s: string) return std_logic_vector is 
        variable slv: std_logic_vector(s'high-s'low downto 0);
        variable k: integer;
    begin
         k := s'high-s'low;
         for i in s'range loop
             slv(k) := to_std_logic(s(i));
             k      := k - 1;
         end loop;
         return slv;
    end to_std_logic_vector;                                       
