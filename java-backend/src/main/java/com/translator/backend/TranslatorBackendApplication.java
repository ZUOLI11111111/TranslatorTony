package com.translator.backend;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

/**
 * 翻译应用Java后端主应用类
 */
@SpringBootApplication
@EnableScheduling
public class TranslatorBackendApplication {

    public static void main(String[] args) {
        SpringApplication.run(TranslatorBackendApplication.class, args);
    }
} 