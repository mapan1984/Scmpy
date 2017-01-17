;;;;;;;;;;;;;;; 表达式的表示

;; 辅助函数: 判断表exp的开头是否为给定符号tag
(define (tagged-list? exp tag)
  (if (pair? exp)
      (eq? (car exp) tag)
      false))


;;;;; 自求值表达式
(define (self-evaluating? exp)
  (cond ((number? exp) true) ; 数字
        ((string? exp) true) ; 字符串
        (else false)))


;;;;; 变量
(define (variable? exp) (symbol? exp)) ; 符号


;;;;; 引号表达式: (quote <text-of-quotation>)
(define (quoted? exp)
  (tagged-list? exp 'quote))

(define (text-of-quotation exp) (cadr exp))


;;;;; 赋值: (set! <var> <value>)
(define (assignment? exp)
  (tagged-list? exp 'set!))

(define (assignment-variable exp) (cadr exp))

(define (assignment-value exp) (caddr exp))


;;;;; 定义:
; (define <var> <value>)
;
; 或者:
;
; (define (<var> <parameter> ... <parameter>)
;   <body>)
; 等价于: 
; (define <var>
;   (lambda (<parameter> ... <parameter>)
;     <body>))
(define (definition? exp)
  (tagged-list? exp 'define))

(define (definition-variable exp)
  (if (symbol? (cadr exp)) ; 是否为lambda
      (cadr exp)
      (caadr exp)))

(define (definition-value exp)
  (if (symbol? (cadr exp))
      (caddr exp)
      (make-lambda (cdadr exp)   ; formal parameters
                   (cddr exp)))) ; body


;;;;; if表达式: (if <predicate> <consequent> <alternative>)
(define (if? exp) (tagged-list? exp 'if))

(define (if-predicate exp) (cadr exp))

(define (if-consequent exp) (caddr exp))

(define (if-alternative exp)
  (if (not (null? (cdddr exp)))
      (cadddr exp)
      'false))  ; 如果没有alternative,返回false

(define (make-if predicate consequent alternative)
  (list 'if predicate consequent alternative))


;;;;; lambda表达式: (lambda (<parameter> ... <parameter>) <body>)
(define (lambda? exp) (tagged-list? exp 'lambda))

(define (lambda-parameters exp) (cadr exp))

(define (lambda-body exp) (cddr exp))

(define (make-lambda parameters body)
  (cons 'lambda (cons parameters body)))


;;;;; begine表达式: (begin <action> ... )
(define (begin? exp) (tagged-list? exp 'begin))

(define (begin-actions exp) (cdr exp))

(define (last-exp? seq) (null? (cdr seq)))

(define (first-exp seq) (car seq))

(define (rest-exps seq) (cdr seq))

(define (make-begin seq) (cons 'begin seq))

(define (sequence->exp seq) ; 把序列变换为表达式
  (cond ((null? seq) seq)
        ((last-exp? seq) (first-exp seq))
        (else (make-begin seq))))


;;;;; cond表达式
(define (cond? exp) (tagged-list? exp 'cond))

(define (cond-clauses exp) (cdr exp))

(define (cond-predicate clause) (car clause))

(define (cond-else-clause? clause)
  (eq? (cond-predicate clause) 'else))

(define (cond-actions clause) (cdr clause))

(define (cond->if exp) ; 将cond表达式exp转换为if表达式
  (expand-clauses (cond-clauses exp)))

(define (expand-clauses clauses)
  (if (null? clauses)
      false
      (let ([first (car clauses)]
            [rest (cdr clauses)])
        (if (cond-else-clause? first)
            (if (null? rest)
                (sequence->exp (cond-clauses first))
                (error "ELSE clause isn't last -- COND->IF" clauses))
            (make-if (cond-predicate first)
                     (sequence->exp (cond-actions first))
                     (expand-clauses rest))))))


;;;;; 过程应用: (operator operands)
(define (application? exp) (pair? exp))

(define (operator exp) (car exp))

(define (operands exp) (cdr exp))

(define (no-operands? ops) (null? ops))

(define (first-operand ops) (car ops))

(define (rest-operands ops) (cdr ops))


;;;;; 复合过程的表示:(procedure <parameters> <body> <env>)
(define (make-procedure parameters body env)
  (list 'procedure parameters body env))

(define (compound-procedure? p)
  (tagged-list? p 'procedure))

(define (procedure-parameters p) (cadr p))

(define (procedure-body p) (caddr p))

(define (procedure-environment p) (cadddr p))


;;;;; 基本过程: (primitive <procedure>)
(define (primitive-procedure? proc)
  (tagged-list? proc 'primitive))

(define (primitive-implementation proc) (cadr proc))

(define primitive-procedures
  (list (list '+ +)
        (list '- -)
        (list '* *)
        (list '/ /)
        (list '= =)
        (list 'car car)
        (list 'cdr cdr)
        (list 'cons cons)
        (list 'null? null?)
        ))

;; ('+ '- '* '/ '= 'car 'cdr 'cons 'null?)
(define (primitive-procedure-names)
  (map car
       primitive-procedures))

;; (('primitive +) ('primitive -) ('primitive *) ('primitive /) ('primitive =) ('primitive car) ('primitive cdr) ('cons cons) ('null? null))
(define (primitive-procedure-objects)
  (map (lambda (proc) (list 'primitive (cadr proc)))
       primitive-procedures))

;; 应用基本过程，apply-in-underlying-scheme保存原来的apply，为了避免与自定义apply同名
(define (apply-primitive-procedure proc args)
  (apply-in-underlying-scheme
    (primitive-implementation proc) args))


;;;;; 谓词检测
(define true #t)

(define false #f)

(define (true? x)
  (not (eq? x false)))

(define (false? x)
  (eq? x false))
