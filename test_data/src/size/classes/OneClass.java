package size.classes;

import common.TestBase;

public class OneClass extends TestBase {
    public static void main(String[] args) {
        OneClass instance = new OneClass();
        System.out.println("One instance created");
        printSizeByClasses(OneClass.class);
        OneClass secondInstance = new OneClass();
        System.out.println("One more instance created");
        printSizeByClasses(OneClass.class);
    }
}
