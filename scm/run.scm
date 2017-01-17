;; 保存原来的apply过程，避免自定义apply覆盖
(define apply-in-underlying-scheme apply)

(load "eval-apply.scm")


;;;;;; 创建初始环境
(define (setup-environment)
  (let ([initial-env 
         (extend-environment (primitive-procedure-names)
                             (primitive-procedure-objects)
                             the-empty-environment)])
    (define-variable! 'true true initial-env)
    (define-variable! 'false false initial-env)
    initial-env))

(define the-global-environment (setup-environment))


;;;;; 循环驱动(读入-求值-打印)
(define input-prompt ";;; m-eval input: ")
(define output-prompt ";;; m-eval value: ")

(define (driver-loop)
  (prompt-for-input input-prompt)
  (let ([input (read)])
    (let ([output (eval input the-global-environment)])
      (announce-ouput output-prompt)
      (user-print output)))
  (driver-loop))

(define (prompt-for-input string)
  (newline) (newline) (display string) (newline))

(define (announce-ouput string)
  (newline) (display string) (newline))

(define (user-print object)
  (if (compound-procedure? object)
      (display (list 'compound-procedure
                     (procedure-parameters object)
                     (procedure-body object)
                     '<procedure-env>))
      (display object)))


;;;;; 启动解释器
(driver-loop)
